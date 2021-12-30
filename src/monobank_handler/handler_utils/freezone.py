handlers = []
webhook_handlers = []


def add_handler(func, amount, comment, may_be_bigger):
    handlers.append([func, amount, comment, may_be_bigger])


def add_webhook_handler(func, amount, comment, may_be_bigger, account):
    webhook_handlers.append([func, amount, comment, may_be_bigger, account])
