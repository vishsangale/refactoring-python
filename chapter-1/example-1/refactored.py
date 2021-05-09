from collections import namedtuple
from dataclasses import dataclass


@dataclass
class StatementData:
    customer: str
    performances: list
    total_amount: int = 0
    total_volume_credits: int = 0


class PerformanceCalculator(object):
    def __init__(self, play_type, performance):
        self.play_type = play_type
        self.performance = performance

    @property
    def amount(self):
        raise TypeError(f"Responsibility of a subclass")

    @property
    def volume_credits(self):
        result = max(self.performance.audience - 30, 0)
        return result


class TragedyCalculator(PerformanceCalculator):
    def __init__(self, performance, play_type):
        super().__init__(play_type, performance)
        self.performance = performance

    @property
    def amount(self):
        result = 40000
        if self.performance.audience > 30:
            result += 1000 * (self.performance.audience - 30)
        return result


class ComedyCalculator(PerformanceCalculator):
    def __init__(self, performance, play_type):
        super().__init__(play_type, performance)
        self.performance = performance

    @property
    def amount(self):
        result = 30000
        if self.performance.audience > 20:
            result += 10000 + 500 * (self.performance.audience - 20)
        result += 300 * self.performance.audience
        return result

    @property
    def volume_credits(self):
        return super().volume_credits + self.performance.audience // 5


def usd(amount):
    amount = amount / 100
    return f"${amount:,.2f}"


def create_performance_calculator(performance, play_type):
    if play_type == "tragedy":
        return TragedyCalculator(performance, play_type)
    if play_type == "comedy":
        return ComedyCalculator(performance, play_type)
    raise TypeError(f"unknown type: {play_type}")


def enrich_performance(performance, plays):
    PerformanceResult = namedtuple(
        "Performance",
        ["play", "amount", "volume_credits", "audience", "play_id", "calculator"],
    )
    audience = performance.audience
    play_id = performance.play_id
    calculator = create_performance_calculator(
        performance, plays[performance.play_id].type
    )
    amount = calculator.amount
    volume_credits = calculator.volume_credits

    return PerformanceResult(
        plays[performance.play_id],
        amount,
        volume_credits,
        audience,
        play_id,
        calculator,
    )


def statement(invoice, plays):
    statement_data = create_statement_data(invoice, plays)
    return render_plain_text(statement_data)


def create_statement_data(invoice, plays):
    statement_data = StatementData(
        invoice.customer,
        [
            enrich_performance(performance, plays)
            for performance in invoice.performances
        ],
    )
    statement_data.total_amount = total_amount(statement_data)
    statement_data.total_volume_credits = total_volume_credits(statement_data)
    return statement_data


def render_plain_text(data):
    result = f"Statement for {data.customer}\n"
    for perf in data.performances:
        result += f"    {perf.play.name}: {usd(perf.amount)} ({perf.audience} seats)\n"
    result += f"Amount owed is {usd(data.total_amount)}\n"
    result += f"You earned {data.total_volume_credits} credits"
    return result


def total_amount(data):
    result = 0
    for perf in data.performances:
        result += perf.calculator.amount
    return result


def total_volume_credits(data):
    result = 0
    for perf in data.performances:
        result += perf.calculator.volume_credits
    return result
