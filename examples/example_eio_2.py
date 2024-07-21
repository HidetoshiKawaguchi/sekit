# -*- coding:utf-8 -*-
import pandas as pd

from sekit.eio import eio


@eio()
def example_eio_2(
    hidden_layer_sizes: list[int], activation: str, validation_fraction: float
) -> tuple[dict[str, list[int] | str | float] | pd.DataFrame]:
    dict_out = {
        "a": [a * 2 for a in hidden_layer_sizes],
        "b": "___" + activation + "___",
        "c": validation_fraction * 3,
    }
    df_out = pd.DataFrame(
        {
            "a": [hidden_layer_sizes[0]],
            "b": ["___" + activation + "___"],
            "c": [validation_fraction * 3],
        }
    )
    return dict_out, df_out


if __name__ == "__main__":
    example_eio_2(
        hidden_layer_sizes=[100, 200],
        activation="relu",
        validation_fraction=0.1,
    )
