from pinsy import Pins


def main():
    pins = Pins(color_mode=8)
    plum = pins.create_ansi_fmt("plum")

    program = "Pinsy v0.1"

    print(plum % program)
    print("This CLI is currently under development.")