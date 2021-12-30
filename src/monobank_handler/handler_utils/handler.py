from monobank_handler.transport import api_request
from monobank_handler.utils import get_utc
from .freezone import handlers
import asyncio

already_proc = []


class CheckPayHandler:
    url = "/personal/statement/{0}/{1}"

    async def idle(self, account="0"):
        self.start_point = get_utc() - 20
        self.account = account
        await self.__check_pay_handler()

    async def start(self, account="0"):
        await self.idle(account)

    def run(self, account="0"):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.idle(account))

    def _get_headers(self, url) -> dict:
        raise NotImplementedError("Please implement _get_headers")

    async def __check_pay_handler(self):

        while True:
            if get_utc() - self.start_point > 100:
                self.start_point = get_utc() - 20

            await asyncio.sleep(60)

            if handlers:
                headers = self._get_headers(CheckPayHandler.url.format(self.account, self.start_point))
                req = api_request("GET", f"/personal/statement/{self.account}/{self.start_point}", headers=headers)
                if not req:
                    continue
                for answer in req:
                    for handler in handlers:
                        func, amount, comment, may_be_bigger = handler
                        if answer["id"] in already_proc:
                            continue
                        already_proc.append(answer["id"])
                        if amount == abs(answer["amount"]) or (amount <= abs(answer["amount"]) and may_be_bigger):
                            if comment:
                                try:
                                    if comment != answer["comment"]:
                                        continue
                                except KeyError:
                                    continue
                            if asyncio.iscoroutinefunction(func):
                                loop = asyncio.get_event_loop()
                                loop.create_task(func(answer))
                            else:
                                func(answer)


#   {'id': 'WD06LyvgYq8m5x2D', 'time': 1640816055, 'description': 'Максим Кривий', 'comment': 'даун', 'mcc': 4829,
#   'originalMcc': 4829, 'amount': -10, 'operationAmount': -10, 'currencyCode': 980, 'commissionRate': 0,
#   'cashbackAmount': 0, 'balance': 28250, 'hold': True, 'receiptId': '93C1-35ME-31PX-C89B'}
