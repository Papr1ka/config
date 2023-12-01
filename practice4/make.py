import auto


# noinspection PyStatementEffect
@auto.cli
@auto.view
@auto.configure(print_tasks=False, mock_name="demo.json")
def test():
    "test" <= ("test2")
    ['echo "test"']

    "test2" <= ("test3")
    ['echo "test2"']

    "test3" <= ("test")
    ['echo "test3"']

    "sw"
    [
        'echo Hello there!',
        'sleep 2',
        'echo "Oops! I fell asleep for a couple seconds!"'
    ]

    "create_venv"
    [
        "python -m venv venv"
    ]

    "graphviz" <= ("create_venv")
    [
        "python -m pip install graphviz"
    ]

    "sstack" <= ("create_venv")
    [
        "python -m pip install -i https://test.pypi.org/simple/ sstack==0.0.1"
    ]

    "venv" <= ("graphviz", "sstack")
    [
        "source venv/bin/activate"
    ]

