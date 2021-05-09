import json
from collections import namedtuple
from pathlib import Path

import original
import refactored


def load(plays_filename: str, invoice_filename: str):
    with Path(plays_filename).open("r") as f:
        play_data = json.load(f)
    plays = {}
    Play = namedtuple("Play", ["name", "type"])
    for play_id, data in play_data.items():
        plays[play_id] = Play(name=data["name"], type=data["type"])

    with Path(invoice_filename).open("r") as f:
        invoice_data = json.load(f)

    Invoice = namedtuple("Invoice", ["customer", "performances"])
    Performance = namedtuple("Performance", ["play_id", "audience"])
    invoices = []
    for invoice in invoice_data:
        performances = []
        for performance in invoice["performances"]:
            performances.append(
                Performance(play_id=performance["playID"], audience=performance["audience"])
            )
        invoices.append(
            Invoice(
                customer=invoice["customer"], performances=performances
            )
        )

    return invoices[0], plays


def test():
    invoice, plays = load("chapter-1/example-1/plays.json", "chapter-1/example-1/invoices.json")

    result = original.statement(invoice, plays)

    assert (
        result == "Statement for BigCo\n"
        "    Hamlet: $650.00 (55 seats)\n"
        "    As You Like It: $580.00 (35 seats)\n"
        "    Othello: $500.00 (40 seats)\n"
        "Amount owed is $1,730.00\n"
        "You earned 47 credits"
    )


def test_refactored():
    invoice, plays = load("chapter-1/example-1/plays.json", "chapter-1/example-1/invoices.json")

    result = refactored.statement(invoice, plays)

    assert (
        result == "Statement for BigCo\n"
        "    Hamlet: $650.00 (55 seats)\n"
        "    As You Like It: $580.00 (35 seats)\n"
        "    Othello: $500.00 (40 seats)\n"
        "Amount owed is $1,730.00\n"
        "You earned 47 credits"
    )