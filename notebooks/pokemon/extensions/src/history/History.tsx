import React, { FC, useEffect, useState, useRef } from "react";
import { WidgetPluginProps, getPage } from "@activeviam/activeui-sdk";
import { Table, Tag } from 'antd';
import useComponentSize from "@rehooks/component-size";
import { widgetKey as battleWidgetKey } from "../battle/pluginWidgetBattle";

export const History: FC<WidgetPluginProps> = (props: any) => {

  const container = useRef<HTMLDivElement>(null);
  const { height } = useComponentSize(container);

  const [history, setHistory] = useState<Object[]>([]);
  const [start, setStart] = useState(false);

  const pageState = getPage(props.dashboardState, props.pageKey);
  const battleWidgetState = Object.values(pageState ? pageState.content : []).find(entry => entry.widgetKey === battleWidgetKey);

  useEffect(() => {
    if (battleWidgetState) {
      const { winner, pokemon, opponentPokemon } = battleWidgetState;

      if (winner === "pending") {
        setStart(true);
      }

      if (start && pokemon && opponentPokemon && winner && winner !== "pending") {
        setHistory(prevHistory => [ 
          { battle: `${pokemon} VS ${opponentPokemon}`, result: (pokemon === winner) ? "WIN" : "LOSE" },
          ...prevHistory, 
        ])
      }
    }
  }, [battleWidgetState])

  const columns = [
    {
      title: "Battle",
      dataIndex: "battle",
      key: "battle",
    },
    {
      title: "Result",
      dataIndex: "result",
      key: "result",
      render: result => {
        const color = (result === "WIN") ? "green" : "volcano";
        return <Tag color={color} key={result}>{result}</Tag>
      },
      width: "70px",
    }
  ]
  
  return (
    <div ref={container} style={{padding:'15px 20px 0px 20px', height: "100%"}}>
      { history && history.length > 0
        ? <Table 
            columns={columns} 
            dataSource={history} 
            pagination={false} 
            showHeader={false} 
            scroll={{ y: height - 40 }}
          />
        : "No battles yet!"
      }
    </div>
  );
};
