import { AWidgetState } from "@activeviam/activeui-sdk";

export interface BattleWidgetState extends AWidgetState {
  winner: string;
  pokemon: string;
  opponentPokemon: string;
}