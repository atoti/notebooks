import { WidgetPlugin, pluginMenuItemRemoveWidget, pluginTitleBarButtonFullScreen } from "@activeviam/activeui-sdk";
import { Battle } from "./Battle";
import { IconBattle } from "./IconBattle";
import { BattleWidgetState } from "./battle.types";

export const widgetKey = "battle";

export const initialState = {
  winner: "",
  pokemon: "",
  opponentPokemon: "",
}

export const pluginWidgetBattle: WidgetPlugin<BattleWidgetState> = {
  Component: Battle,
  Icon: IconBattle,
  initialState: {
    widgetKey,
    ...initialState
  },
  key: widgetKey,
  menuItems: [pluginMenuItemRemoveWidget.key],
  titleBarButtons: [pluginTitleBarButtonFullScreen.key],
  contextMenuItems: [],
  translations: {
    "en-US": {
      key: "Battle",
      defaultName: "New Battle"
    }
  },
}
