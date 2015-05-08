__author__ = 'Brycon'

import player_controller
import player_model


def main():
    model = player_model.Model()
    controller = player_controller.Controller(model)

    controller.show()


if __name__ == "__main__":
    main()