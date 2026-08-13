"""Toolkit for the retail domain."""

import json
from typing import List

from tau2.domains.retail_ja.data_model import (
    GiftCard,
    Order,
    OrderPayment,
    PaymentMethod,
    Product,
    RetailDB,
    User,
    UserAddress,
    Variant,
)
from tau2.domains.retail_ja.utils import RETAIL_DB_PATH
from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool


class RetailTools(ToolKitBase):  # Tools
    """All the tools for the retail domain."""

    db: RetailDB

    def __init__(self, db: RetailDB) -> None:
        super().__init__(db)

    def _get_order(self, order_id: str) -> Order:
        """Get the order from the database.

        Args:
            order_id: The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.

        Returns:
            The order.

        Raises:
            ValueError: If the order is not found.
        """
        if order_id not in self.db.orders:
            raise ValueError("Order not found")
        return self.db.orders[order_id]

    def _get_user(self, user_id: str) -> User:
        """Get the user from the database.

        Args:
            user_id: The user id, such as 'sara_doe_496'.

        Returns:
            The user.

        Raises:
            ValueError: If the user is not found.
        """
        if user_id not in self.db.users:
            raise ValueError("User not found")
        return self.db.users[user_id]

    def _get_product(self, product_id: str) -> Product:
        """Get the product from the database.

        Args:
            product_id: The product id, such as '6086499569'. Be careful the product id is different from the item id.

        Returns:
            The product.

        Raises:
            ValueError: If the product is not found.
        """
        if product_id not in self.db.products:
            raise ValueError("Product not found")
        return self.db.products[product_id]

    def _get_item(self, item_id: str) -> Variant:
        """Get the item from the database.

        Args:
            item_id: The item id, such as '6086499569'. Be careful the item id is different from the product id.

        Returns:
            The item.

        Raises:
            ValueError: If the item is not found.
        """
        for _, product in self.db.products.items():
            if item_id in product.variants:
                return product.variants[item_id]

        raise ValueError("Item not found")

    def _get_variant(self, product_id: str, variant_id: str) -> Variant:
        """Get the variant from the database.

        Args:
            product_id: The product id, such as '6086499569'. Be careful the product id is different from the item id.
            variant_id: The variant id, such as '1008292230'.

        Returns:
            The variant.

        Raises:
            ValueError: If the variant is not found.
        """
        product = self._get_product(product_id)
        if variant_id not in product.variants:
            raise ValueError("Variant not found")
        return product.variants[variant_id]

    def _get_payment_method(
        self, user_id: str, payment_method_id: str
    ) -> PaymentMethod:
        """Get the payment method from the database.

        Args:
            payment_method_id: The payment method id, such as 'gift_card_0000000' or 'credit_card_0000000'.

        Returns:
            The payment method.

        Raises:
            ValueError: If the payment method is not found.
        """
        user = self._get_user(user_id)
        if payment_method_id not in user.payment_methods:
            raise ValueError("Payment method not found")
        return user.payment_methods[payment_method_id]

    def _is_pending_order(self, order: Order) -> bool:
        """Check if the order is pending. This is not a strict check, and not meant to be used for modify_items in pending orders.

        Args:
            order: The order.
        """
        return "保留中" in order.status

    @is_tool(ToolType.GENERIC)
    def calculate(self, expression: str) -> str:
        """
        数式の計算結果を算出します。

        Args:
            expression: 計算する数式（例: '2 + 2'）。数式には、数値、演算子（+, -, *, /）、括弧、スペースを含めることができます。
        
        Returns:
            The result of the mathematical expression.

        Raises:
            ValueError: If the expression is invalid.
        """
        if not all(char in "0123456789+-*/(). " for char in expression):
            raise ValueError("Invalid characters in expression")
        return str(round(float(eval(expression, {"__builtins__": None}, {})), 2))

    @is_tool(ToolType.WRITE)
    def cancel_pending_order(self, order_id: str, reason: str) -> Order:
        """
        保留中の注文をキャンセルします。注文がすでに処理済み、
        または配送済みの場合はキャンセルできません。エージェントはキャンセルの詳細を説明し、
        処理を進めるためにユーザーに明示的な確認を求める必要があります。
        ユーザーが同意した場合、注文ステータスは「キャンセル済み」に変更され、代金が払い戻されます。
        決済にギフトカードが使用されていた場合、払い戻しは即座にユーザーのギフトカード残高に追加されます。
        それ以外の場合、払い戻しの処理には5〜7営業日かかります。この関数は、キャンセル後の注文詳細を返します。

        Args:
            order_id: 注文ID（例: '#W0000000'）。注文IDの先頭に「#」記号があることに注意してください。
            reason: キャンセルの理由。'不要になった'または '間違えて注文した'のいずれかである必要があります。
        Returns:
            Order: The order details after the cancellation.
        """
        # check order exists and is pending
        order = self._get_order(order_id)
        if order.status != "保留中":
            raise ValueError("Non-pending order cannot be cancelled")

        # check reason
        if reason not in {"不要になった", "間違えて注文した"}:
            raise ValueError("Invalid reason")

        # handle refund
        refunds = []
        for payment in order.payment_history:
            payment_id = payment.payment_method_id
            refund = OrderPayment(
                transaction_type="refund",
                amount=payment.amount,
                payment_method_id=payment_id,
            )
            refunds.append(refund)
            user = self._get_user(order.user_id)
            payment_method = self._get_payment_method(user.user_id, payment_id)
            if isinstance(payment_method, GiftCard):  # refund to gift card immediately
                payment_method.balance += payment.amount
                payment_method.balance = round(payment_method.balance, 2)

        # update order status
        order.status = "キャンセル済み"
        order.cancel_reason = reason
        order.payment_history.extend(refunds)

        return order

    @is_tool(ToolType.WRITE)
    def exchange_delivered_order_items(
        self,
        order_id: str,
        item_ids: List[str],
        new_item_ids: List[str],
        payment_method_id: str,
    ) -> Order:
        """配達済みの注文の商品を、同じ製品タイプの新しい商品に交換します。
        配達済みの注文に対しては、エージェントによる返品または交換は1回のみ行うことができます。
        エージェントは交換の詳細を説明し、処理を進めるためにユーザーから明示的な同意を得る必要があります。

        Args:
            order_id: '#W0000000' のような注文ID。注文IDの先頭に「#」記号があることに注意してください。
            item_ids: 交換対象の商品ID。それぞれ '1008292230' のような形式です。リスト内に重複する商品が含まれる可能性があります。
            new_item_ids: 交換先となる新しい商品ID。それぞれ '1008292230' のような形式です。
                         リスト内に重複する商品が含まれる可能性があります。各新しい商品IDは、
                         同じ位置にある商品IDと一致し、かつ同じ製品のものである必要があります。
            payment_method_id: 商品の価格差額を支払う、または返金を受け取るための決済手段ID。
                             'gift_card_0000000' や 'credit_card_0000000' など。これらはユーザーまたは
                             注文の詳細から確認できます。
        Returns:
            Order: The order details after the exchange.

        Raises:
            ValueError: If the order is not delivered.
            ValueError: If the items to be exchanged do not exist.
            ValueError: If the new items do not exist or do not match the old items.
            ValueError: If the number of items to be exchanged does not match.
        """
        # check order exists and is delivered
        order = self._get_order(order_id)
        if order.status != "配達済み":
            raise ValueError("Non-delivered order cannot be exchanged")

        # check the items to be exchanged exist. There can be duplicate items in the list.
        all_item_ids = [item.item_id for item in order.items]
        for item_id in item_ids:
            if item_ids.count(item_id) > all_item_ids.count(item_id):
                raise ValueError(f"Number of {item_id} not found.")

        # check new items exist and match old items and are available
        if len(item_ids) != len(new_item_ids):
            raise ValueError("The number of items to be exchanged should match.")

        diff_price = 0
        for item_id, new_item_id in zip(item_ids, new_item_ids):
            item = next((item for item in order.items if item.item_id == item_id), None)
            if item is None:
                raise ValueError(f"Item {item_id} not found")
            product_id = item.product_id
            variant = self._get_variant(product_id, new_item_id)
            if not variant.available:
                raise ValueError(f"New item {new_item_id} not found or available")

            old_price = item.price
            new_price = variant.price
            diff_price += new_price - old_price

        diff_price = round(diff_price, 2)

        # check payment method exists and can cover the price difference if gift card
        payment_method = self._get_payment_method(order.user_id, payment_method_id)

        if isinstance(payment_method, GiftCard) and payment_method.balance < diff_price:
            raise ValueError(
                "Insufficient gift card balance to pay for the price difference"
            )

        # modify the order
        order.status = "交換リクエスト済み"
        order.exchange_items = sorted(item_ids)
        order.exchange_new_items = sorted(new_item_ids)
        order.exchange_payment_method_id = payment_method_id
        order.exchange_price_difference = diff_price

        return order

    @is_tool(ToolType.READ)
    def find_user_id_by_name_zip(
        self, first_name: str, last_name: str, zip: str
    ) -> str:
        """名、姓、郵便番号からユーザーIDを検索します。
        ユーザーが見つからない場合、この関数はエラーメッセージを返します。デフォルトでは、メールアドレスで
        ユーザーIDを検索するため、メールアドレスでユーザーが見つからない場合、またはユーザーが
        メールアドレスを覚えていない場合にのみ、この関数を呼び出してください。

        Args:
            first_name: 顧客のファーストネーム（名）。'太郎' など。
            last_name: 顧客のラストネーム（姓）。'田中' など。
            zip: 顧客の郵便番号。'123-4567' など。

        Returns:
            str: The user id if found, otherwise an error message.

        Raises:
            ValueError: If the user is not found.
        """
        for user_id, user in self.db.users.items():
            if (
                user.name.first_name.lower() == first_name.lower()
                and user.name.last_name.lower() == last_name.lower()
                and user.address.zip == zip
            ):
                return user_id
        raise ValueError("User not found")

    @is_tool(ToolType.READ)
    def find_user_id_by_email(self, email: str) -> str:
        """メールアドレスからユーザーIDを検索します。ユーザーが見つからない場合、この関数はエラーメッセージを返します。

        Args:
            email: ユーザーのメールアドレス。'something@example.com' など。

        Returns:
            str: The user id if found, otherwise an error message.

        Raises:
            ValueError: If the user is not found.
        """
        for user_id, user in self.db.users.items():
            if user.email.lower() == email.lower():
                return user_id
        raise ValueError("User not found")

    @is_tool(ToolType.READ)
    def get_order_details(self, order_id: str) -> Order:
        """注文のステータスと詳細を取得します。

        Args:
            order_id: '#W0000000' のような注文ID。注文IDの先頭に「#」記号があることに注意してください。

        Returns:
            Order: The order details.

        Raises:
            ValueError: If the order is not found.
        """
        order = self._get_order(order_id)
        return order

    @is_tool(ToolType.READ)
    def get_product_details(self, product_id: str) -> Product:
        """製品の在庫詳細を取得します。

        Args:
            product_id: '6086499569' のような製品ID。製品IDは商品ID（item id）とは異なることに注意してください。

        Returns:
            Product: The product details.

        Raises:
            ValueError: If the product is not found.
        """
        product = self._get_product(product_id)
        return product

    @is_tool(ToolType.READ)
    def get_item_details(self, item_id: str) -> Variant:
        """商品の在庫詳細を取得します。

        Args:
            item_id: '6086499569' のような商品ID。商品IDは製品ID（product id）とは異なることに注意してください。

        Returns:
            Variant: The item details.

        Raises:
            ValueError: If the item is not found.
        """
        item = self._get_item(item_id)
        return item

    @is_tool(ToolType.READ)
    def get_user_details(self, user_id: str) -> User:
        """ユーザーの詳細（注文履歴を含む）を取得します。

        Args:
            user_id: 'sara_doe_496' のようなユーザーID。

        Returns:
            User: The user details.

        Raises:
            ValueError: If the user is not found.
        """
        user = self._get_user(user_id)
        return user

    @is_tool(ToolType.READ)
    def list_all_product_types(self) -> str:
        """すべての製品タイプの名称と製品IDを一覧表示します。
        各製品には、ユニークな商品IDとオプションを持つ、さまざまな異なる商品があります。
        ストア内には50種類の製品のみが存在します。

        Returns:
            str: A JSON string mapping product names to their product IDs, sorted alphabetically by name.
        """
        product_dict = {
            product.name: product.product_id for product in self.db.products.values()
        }
        return json.dumps(product_dict, sort_keys=True, ensure_ascii=False)

    @is_tool(ToolType.WRITE)
    def modify_pending_order_address(
        self,
        order_id: str,
        address1: str,
        address2: str,
        city: str,
        state: str,
        country: str,
        zip: str,
    ) -> Order:
        """保留中（未発送）の注文の配送先住所を変更します。
        エージェントは変更の詳細を説明し、処理を進めるためにユーザーから明示的な同意を得る必要があります。

        Args:
            order_id: '#W0000000' のような注文ID。注文IDの先頭に「#」記号があることに注意してください。
            address1: 住所の1行目。'1-2-3' など。
            address2: 住所の2行目。'丸の内マンション 100' や空文字 '' など。
            city: 市区町村。'千代田区丸の内' など。
            state: 州・都道府県。'東京都' など。
            country: 国。'日本' など。
            zip: 郵便番号。'123-4567' など。

        Returns:
            Order: The order details after the modification.

        Raises:
            ValueError: If the order is not pending.
        """
        # Check if the order exists and is pending
        order = self._get_order(order_id)
        if not self._is_pending_order(order):
            raise ValueError("Non-pending order cannot be modified")

        # Modify the address
        order.address = UserAddress(
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            country=country,
            zip=zip,
        )
        return order

    @is_tool(ToolType.WRITE)
    def modify_pending_order_items(
        self,
        order_id: str,
        item_ids: List[str],
        new_item_ids: List[str],
        payment_method_id: str,
    ) -> Order:
        """保留中（未発送）の注文の商品を、同じ製品でオプションが異なる新しい商品に変更します。
        保留中の注文に対して、この関数は1回のみ呼び出すことができます。
        エージェントは変更の詳細を説明し、処理を進めるためにユーザーから明示的な同意を得る必要があります。

        Args:
            order_id: '#W0000000' のような注文ID。注文IDの先頭に「#」記号があることに注意してください。
            item_ids: 変更対象の商品ID。それぞれ '1008292230' のような形式です。リスト内に重複する商品が含まれる可能性があります。
            new_item_ids: 変更先となる新しい商品ID。それぞれ '1008292230' のような形式です。
                         リスト内に重複する商品が含まれる可能性があります。各新しい商品IDは、
                         同じ位置にある商品IDと一致し、かつ同じ製品のものである必要があります。
            payment_method_id: 商品の価格差額を支払う、または返金を受け取るための決済手段ID。
                             'gift_card_0000000' や 'credit_card_0000000' など。これらはユーザーまたは
                             注文の詳細から確認できます。

        Returns:
            Order: The order details after the modification.

        Raises:
            ValueError: If the order is not pending.
            ValueError: If the items to be modified do not exist.
            ValueError: If the new items do not exist or do not match the old items.
            ValueError: If the number of items to be modified does not match.
        """

        # Check if the order exists and is pending
        order = self._get_order(order_id)
        if order.status != "保留中":
            raise ValueError("Non-pending order cannot be modified")

        # Check if the items to be modified exist. There can be duplicate items in the list.
        all_item_ids = [item.item_id for item in order.items]
        for item_id in item_ids:
            if item_ids.count(item_id) > all_item_ids.count(item_id):
                raise ValueError(f"{item_id} not found")

        # Check new items exist, match old items, and are available
        if len(item_ids) != len(new_item_ids):
            raise ValueError("The number of items to be exchanged should match")

        diff_price = 0
        for item_id, new_item_id in zip(item_ids, new_item_ids):
            if item_id == new_item_id:
                raise ValueError(
                    "The new item id should be different from the old item id"
                )
            item = next((item for item in order.items if item.item_id == item_id), None)
            if item is None:
                raise ValueError(f"Item {item_id} not found")
            product_id = item.product_id
            variant = self._get_variant(product_id, new_item_id)
            if not variant.available:
                raise ValueError(f"New item {new_item_id} not found or available")

            old_price = item.price
            new_price = variant.price
            diff_price += new_price - old_price

        # Check if the payment method exists
        payment_method = self._get_payment_method(order.user_id, payment_method_id)

        # If the new item is more expensive, check if the gift card has enough balance
        if isinstance(payment_method, GiftCard) and payment_method.balance < diff_price:
            raise ValueError("Insufficient gift card balance to pay for the new item")

        # Handle the payment or refund
        order.payment_history.append(
            OrderPayment(
                transaction_type="payment" if diff_price > 0 else "refund",
                amount=abs(diff_price),
                payment_method_id=payment_method_id,
            )
        )
        if isinstance(payment_method, GiftCard):
            payment_method.balance -= diff_price
            payment_method.balance = round(payment_method.balance, 2)

        # Modify the order
        for item_id, new_item_id in zip(item_ids, new_item_ids):
            item = next((item for item in order.items if item.item_id == item_id), None)
            if item is None:
                raise ValueError(f"Item {item_id} not found")
            item.item_id = new_item_id
            item.price = variant.price
            item.options = variant.options
        order.status = "保留中（アイテム変更済み）"

        return order

    @is_tool(ToolType.WRITE)
    def modify_pending_order_payment(
        self,
        order_id: str,
        payment_method_id: str,
    ) -> Order:
        """保留中（未発送）の注文の決済手段を変更します。
        エージェントは変更の詳細を説明し、処理を進めるためにユーザーから明示的な同意を得る必要があります。

        Args:
            order_id: '#W0000000' のような注文ID。注文IDの先頭に「#」記号があることに注意してください。
            payment_method_id: 商品の価格差額を支払う、または返金を受け取るための決済手段ID。
                             'gift_card_0000000' や 'credit_card_0000000' など。これらはユーザーまたは
                             注文の詳細から確認できます。

        Returns:
            Order: The order details after the modification.

        Raises:
            ValueError: If the order is not pending.
            ValueError: If the payment method does not exist.
            ValueError: If the payment history has more than one payment.
            ValueError: If the new payment method is the same as the current one.
        """
        order = self._get_order(order_id)

        # Check if the order exists and is pending
        if not self._is_pending_order(order):
            raise ValueError("Non-pending order cannot be modified")

        # Check if the payment method exists
        payment_method = self._get_payment_method(order.user_id, payment_method_id)

        # Check that the payment history should only have one payment
        if (
            len(order.payment_history) != 1
            or order.payment_history[0].transaction_type != "payment"
        ):
            raise ValueError("There should be exactly one payment for a pending order")

        # Check that the payment method is different
        if order.payment_history[0].payment_method_id == payment_method_id:
            raise ValueError(
                "The new payment method should be different from the current one"
            )

        amount = order.payment_history[0].amount

        # Check if the new payment method has enough balance if it is a gift card
        if isinstance(payment_method, GiftCard) and payment_method.balance < amount:
            raise ValueError("Insufficient gift card balance to pay for the order")

        # Modify the payment method
        order.payment_history.extend(
            [
                OrderPayment(
                    transaction_type="payment",
                    amount=amount,
                    payment_method_id=payment_method_id,
                ),
                OrderPayment(
                    transaction_type="refund",
                    amount=amount,
                    payment_method_id=order.payment_history[0].payment_method_id,
                ),
            ]
        )

        # If payment is made by gift card, update the balance
        if isinstance(payment_method, GiftCard):
            payment_method.balance -= amount
            payment_method.balance = round(payment_method.balance, 2)

        # If refund is made to a gift card, update the balance
        old_payment_method = self._get_payment_method(
            order.user_id, order.payment_history[0].payment_method_id
        )
        if isinstance(old_payment_method, GiftCard):
            old_payment_method.balance += amount
            old_payment_method.balance = round(old_payment_method.balance, 2)

        return order

    @is_tool(ToolType.WRITE)
    def modify_user_address(
        self,
        user_id: str,
        address1: str,
        address2: str,
        city: str,
        state: str,
        country: str,
        zip: str,
    ) -> User:
        """ユーザーのデフォルトの配送先住所を変更します。
        エージェントは変更の詳細を説明し、処理を進めるためにユーザーから明示的な同意を得る必要があります。

        Args:
            user_id: 'sara_doe_496' のようなユーザーID。。
            address1: 住所の1行目。'1-2-3' など。
            address2: 住所の2行目。'丸の内マンション 100' や空文字 '' など。
            city: 市区町村。'千代田区丸の内' など。
            state: 州・都道府県。'東京都' など。
            country: 国。'日本' など。
            zip: 郵便番号。'123-4567' など。

        Returns:
            User: The user details after the modification.

        Raises:
            ValueError: If the user is not found.
        """
        user = self._get_user(user_id)
        user.address = UserAddress(
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            country=country,
            zip=zip,
        )
        return user

    @is_tool(ToolType.WRITE)
    def return_delivered_order_items(
        self,
        order_id: str,
        item_ids: List[str],
        payment_method_id: str,
    ) -> Order:
        """配達済みの注文の一部商品を返品します。
        注文ステータスは「返品リクエスト済み」に変更されます。
        エージェントは返品の詳細を説明し、処理を進めるためにユーザーから明示的な同意を得る必要があります。
        商品の返品方法および返送先に関するフォローアップメールがユーザーに届きます。

        Args:
            order_id: '#W0000000' のような注文ID。注文IDの先頭に「#」記号があることに注意してください。
            item_ids: 返品対象の商品ID。それぞれ '1008292230' のような形式です。リスト内に重複する商品が含まれる可能性があります。
            payment_method_id: 商品の価格差額を支払う、または返金を受け取るための決済手段ID。
                             'gift_card_0000000' や 'credit_card_0000000' など。これらはユーザーまたは
                             注文の詳細から確認できます。

        Returns:
            Order: The order details after requesting the return.

        Raises:
            ValueError: If the order is not delivered.
            ValueError: If the payment method is not the original payment method or a gift card.
            ValueError: If the items to be returned do not exist.
        """
        order = self._get_order(order_id)
        if order.status != "配達済み":
            raise ValueError("Non-delivered order cannot be returned")

        # Check if the payment method exists and is either the original payment method or a gift card
        user = self._get_user(order.user_id)
        payment_method = self._get_payment_method(user.user_id, payment_method_id)

        if (
            not isinstance(payment_method, GiftCard)
            and payment_method_id != order.payment_history[0].payment_method_id
        ):
            raise ValueError("Payment method should be the original payment method")

        # Check if the items to be returned exist (there could be duplicate items in either list)
        all_item_ids = [item.item_id for item in order.items]
        for item_id in item_ids:
            if item_ids.count(item_id) > all_item_ids.count(item_id):
                raise ValueError("Some item not found")

        # Update the order status
        order.status = "返品リクエスト済み"
        order.return_items = sorted(item_ids)
        order.return_payment_method_id = payment_method_id

        return order

    # @is_tool(ToolType.THINK)
    # def think(self, thought: str) -> str:
    #     """
    #     Use the tool to think about something.
    #     It will not obtain new information or change the database, but just append the thought to the log.
    #     Use it when complex reasoning or some cache memory is needed.

    #     Args:
    #         thought: A thought to think about.

    #     Returns:
    #         Empty string
    #     """
    #     return ""

    @is_tool(ToolType.GENERIC)
    def transfer_to_human_agents(self, summary: str) -> str:
        """ユーザーの問題の要約を添えて、ユーザーを人間のエージェントに転送します。
        以下の場合にのみ転送してください。
         - ユーザーが明示的に人間のエージェントを求めている場合
         - ポリシーおよび利用可能なツールでは、ユーザーの問題を解決できない場合

        Args:
            summary: ユーザーの問題の要約。

        Returns:
            A message indicating the user has been transferred to a human agent.
        """
        return "Transfer successful"


if __name__ == "__main__":
    from tau2.domains.retail_ja.utils import RETAIL_DB_PATH

    retail = RetailTools(RetailDB.load(RETAIL_DB_PATH))
    print(retail.get_statistics())
