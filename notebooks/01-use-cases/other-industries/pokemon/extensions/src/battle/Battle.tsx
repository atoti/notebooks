import React, { FC, useEffect, useState, useRef } from "react";
import useComponentSize from "@rehooks/component-size";
import {
  WidgetPluginProps, parse, useDataModel, getPage, createFilter, DashboardState, MdxExpression, FilterOnMembers,
  HierarchyCoordinates,
} from "@activeviam/activeui-sdk";
import { Button, Select, Space, Card, Typography, Spin } from 'antd';
import produce from "immer";
import * as api from '../api/Api';
import { BattleWidgetState } from "./battle.types";
import { PokemonTile } from "./PokemonTile";
import styles from './battle.module.css';
import { widgetKey as matchupWidgetKey } from "../matchup/pluginWidgetMatchup";
import { createFilterOnMembers } from "./createFilterOnMembers";

const POKEMON_LEVEL: string = "Pokemon";
const OPPONENT_LEVEL: string = "Opponent Pokemon";

export const Battle: FC<WidgetPluginProps<BattleWidgetState>> = (props: any) => {

  const dataModel = useDataModel("default");
  const cube = dataModel.catalogs["atoti"].cubes["Pokemon battles"]

  const [pokemonList, setPokemonList] = useState([]);
  const [selectOptions, setSelectOptions] = useState<{ [key: string]: JSX.Element[] }>({});
  const [pokemon, setPokemon] = useState("");
  const [opponentPokemon, setOpponentPokemon] = useState("");
  const [winner, setWinner] = useState("");
  const [battling, setBattling] = useState(false);

  const container = useRef<HTMLDivElement>(null);
  const { height, width } = useComponentSize(container);

  const selectPokemonRef = useRef<any>(null);
  const [displaySelectPokemon, setDisplaySelectPokemon] = useState(false);
  const selectOpponentRef = useRef<any>(null);
  const [displaySelectOpponent, setDisplaySelectOpponent] = useState(false);

  useEffect(() => {

    const updatedDashboardState = produce(props.dashboardState, (draftDashboardState: DashboardState) => {
      const pageState = getPage(draftDashboardState, props.pageKey);
      if (!pageState) return;

      Object.values(pageState.content).forEach(widget => {
        if (widget.widgetKey === props.widgetState.widgetKey) {
          widget.pokemon = "";
          widget.opponentPokemon = "";
          widget.winner = "pending";
        } else if (widget.widgetKey === matchupWidgetKey) {
          widget.name = "Current Matchup";
        }
      });
    });
    props.onDashboardChange(updatedDashboardState);
    populatePokemonList();
  }, []);

  useEffect(() => {
    populatePokemonSelectOptions();
    if (pokemon) {
      populateOpponentSelectOptions();
    }
  }, [pokemonList])

  useEffect(() => {
    if (pokemon) {
      populateOpponentSelectOptions();
      if (pokemon === opponentPokemon) {
        setOpponentPokemon("");
      }
    }
  }, [pokemon]);

  useEffect(() => {
    if (displaySelectPokemon && selectPokemonRef.current) {
      selectPokemonRef.current.focus();
    }
  }, [displaySelectPokemon])

  useEffect(() => {
    if (displaySelectOpponent && selectOpponentRef.current) {
      selectOpponentRef.current.focus();
    }
  }, [displaySelectOpponent])

  const populatePokemonList = async () => {
    const list = await api.getLevelMembers(POKEMON_LEVEL);
    setPokemonList(list);
  }

  const populatePokemonSelectOptions = () => {
    const selectOptions = generateSelectOptions(pokemonList);

    setSelectOptions(prevOptions => ({
      ...prevOptions,
      [POKEMON_LEVEL]: selectOptions
    }))
  }

  const populateOpponentSelectOptions = () => {
    const selectOptions = generateSelectOptions(
      pokemonList.filter(opponent => opponent !== pokemon)
    );

    setSelectOptions(prevOptions => ({
      ...prevOptions,
      [OPPONENT_LEVEL]: selectOptions
    }))
  }

  const generateSelectOptions = (pokemonList: any[]) => {
    return pokemonList.map((element) => {
      return (
        <Select.Option value={element} label={element}>
          <PokemonTile pokemon={element} />
        </Select.Option>
      )
    });
  }

  const newBattle = () => {
    setPokemon("");
    setOpponentPokemon("");
    setWinner("");
  };

  const handleBattle = async () => {
    setBattling(true);
    const winRate = await api.getWinRate(pokemon, opponentPokemon);
    const rand = Math.floor((Math.random() * 50) + 1);
    const passRate = rand + ((!winRate || winRate == 0.5) ? 25 : (winRate > 0.5) ? 50 : 0);
    const roll = Math.floor((Math.random() * 100) + 1);
    const winner = (roll <= passRate ? pokemon : opponentPokemon);
    await api.addBattle(pokemon, opponentPokemon, winner);

    const updatedDashboardState = produce(props.dashboardState, (draftDashboardState: DashboardState) => {

      const pageState = getPage(draftDashboardState, props.pageKey);
      if (!pageState) return;

      pageState.filters = [
        ...createFilters({ [POKEMON_LEVEL]: pokemon }),
      ];

      pageState.content = Object.fromEntries(Object.entries(pageState.content).map(([key, widget]) => {
        if (widget.widgetKey === matchupWidgetKey) {
          const newState = {
            ...widget,
            name: `${pokemon} VS ${opponentPokemon}`,
            filters: [
              ...createFilters({ [POKEMON_LEVEL]: pokemon, [OPPONENT_LEVEL]: opponentPokemon }),
            ]
          }
          return ([key, newState]);
        } else if (widget.widgetKey === props.widgetState.widgetKey) {
          const newState = {
            ...widget,
            pokemon,
            opponentPokemon,
            winner
          }
          return ([key, newState]);
        }
        return ([key, widget]);
      }));
    });
    props.onDashboardChange(updatedDashboardState);
    setWinner(winner);
    setBattling(false);
  }

  const createFilters = (obj: any) => {
    return Object.entries(obj).map(([key, value]) => createFilterOnMembers(key, value));
  }

  return (
    <div ref={container} style={{ padding: '20px', height: "100%", width: "100%" }}>
      <div style={{ overflow: 'auto', maxHeight: height - 30, maxWidth: width - 10 }}>
        <Space size={32} align="start">
          <span></span>
          {displaySelectPokemon
            ? <Select
              style={{ width: 250 }}
              showSearch
              value={pokemon}
              onChange={(value) => setPokemon(value)}
              onDropdownVisibleChange={visible => { if (!visible) setDisplaySelectPokemon(false) }}
              showAction={["focus", "click"]}
              ref={selectPokemonRef}
              optionLabelProp="label"
              listHeight={window.innerHeight - 400}
            >
              {selectOptions[POKEMON_LEVEL]}
            </Select>
            : <div>
              <img
                className={winner && winner == pokemon ? styles.crownWin : styles.crownLose}
                src={require('../resources/images/crown.png')}
              />
              <Card
                className={!winner ? styles.highlight : winner == pokemon ? styles.win : styles.lose}
                bodyStyle={pokemon ? { padding: "0px" } : { padding: "0px", textAlign: "center", lineHeight: "100px" }}
                onClick={() => { if (!winner && !battling) setDisplaySelectPokemon(true) }}
              >
                {pokemon ? <PokemonTile pokemon={pokemon} /> : "Select Your Pokemon"}
              </Card>
            </div>
          }
          <Typography.Title style={{ lineHeight: "100px" }}>VS</Typography.Title>
          {displaySelectOpponent
            ? <Select
              style={{ width: 250 }}
              showSearch
              value={opponentPokemon}
              onChange={(value) => setOpponentPokemon(value)}
              onDropdownVisibleChange={visible => { if (!visible) setDisplaySelectOpponent(false) }}
              showAction={["focus", "click"]}
              ref={selectOpponentRef}
              optionLabelProp="label"
              listHeight={window.innerHeight - 400}
            >
              {selectOptions[OPPONENT_LEVEL]}
            </Select>
            : <div>
              <img
                className={winner && winner == opponentPokemon ? styles.crownWin : styles.crownLose}
                src={require('../resources/images/crown.png')}
              />
              <Card
                className={!winner ? (pokemon ? styles.highlight : styles.disable) : winner == opponentPokemon ? styles.win : styles.lose}
                bodyStyle={opponentPokemon ? { padding: "0px" } : { padding: "0px", textAlign: "center", lineHeight: "100px" }}
                onClick={() => { if (!winner && pokemon && !battling) setDisplaySelectOpponent(true) }}
              >
                {opponentPokemon ? <PokemonTile pokemon={opponentPokemon} /> : "Select Opponent Pokemon"}
              </Card>
            </div>
          }
          <div style={{ height: "100px", position: "relative" }}>
            {battling
              ? <span style={{ margin: "0px", position: "absolute", top: "50%", transform: "translateY(-50%)", whiteSpace: "nowrap" }}>
                <Spin style={{ marginRight: "15px" }} />Battling ...
              </span>
              : winner
                ? <span style={{ margin: "0px", position: "absolute", top: "50%", transform: "translateY(-50%)" }}><Button
                  size="large"
                  onClick={() => newBattle()}
                >
                  Again!
                </Button></span>
                : <span style={{ margin: "0px", position: "absolute", top: "50%", transform: "translateY(-50%)" }}><Button
                  size="large"
                  type="primary"
                  onClick={() => handleBattle()}
                  disabled={!pokemon || !opponentPokemon || pokemon == opponentPokemon}
                >
                  Battle!
                </Button></span>
            }
          </div>
        </Space>
      </div>
    </div>
  );
};
