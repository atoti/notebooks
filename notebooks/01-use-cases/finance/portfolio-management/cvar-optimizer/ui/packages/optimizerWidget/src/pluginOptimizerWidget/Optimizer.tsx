import React, { FC, useEffect, useState, useRef } from "react";
import { useActivePivotClient, useDataModels, useQueryResult, WidgetPluginProps } from "@activeviam/activeui-sdk";
import { Select, Button, message } from 'antd';
import { SettingOutlined } from '@ant-design/icons';
// import 'antd/dist/antd.css';
import axios from "axios";

export const Optimizer: FC<WidgetPluginProps> = (props) => {

    const container = useRef<HTMLDivElement>(null);
    const [portfolioOptions, setPortfolioOptions] = useState<any>();
    const [iterationOptions, setIterationOptions] = useState<any>();
    const [selectedPortfolio, setSelectedPortfolio] = useState<any>();
    const [selectedIteration, setSelectedIteration] = useState<any>("-|Base");
    const [disableIteration, setDisableIteration] = useState<boolean>(true);
    const selectStyles = {
        display: 'inline-block',
    };

    const dataModels = useDataModels();

    if (Object.keys(dataModels).length !== 1) {
        return (<div>Not implemented for multiple servers yet.</div>)
    };
    const serverKey = Object.keys(dataModels)[0];
    const apClient = useActivePivotClient(serverKey);
    const apUrl = `${apClient.url}/atoti/pyapi`;

    const { data: portfolioData } = useQueryResult({
        serverKey: "default",
        queryId: props.queryId,
        query: {
            mdx: "SELECT NON EMPTY [Portfolios Allocation].[Portfolio].[Portfolio].Members ON ROWS FROM [Portfolio optimization]",
            updateMode: "realTime"
        }
    });

    useEffect(() => {
        generateOptions();
    }, [portfolioData]);

    const updateIteration = async () => {
        if (selectedPortfolio != undefined) {
            axios
                .get(`${apUrl}/getIteration/${selectedPortfolio}`).then(response => {
                    if (response) {
                        setIterationOptions(response.data.map((element: string) => {
                            return (
                                <Select.Option value={element} label={element}>
                                    {element}
                                </Select.Option>
                            )
                        }))
                    }
                })
        }
    }

    const generateOptions = () => {

        const dataset = portfolioData;

        if (!dataset) {
            return null;
        }

        console.log("rowsAxis.positions", dataset.axes);
        const [rowsAxis] = dataset.axes;
        const list = rowsAxis.positions.map((position: { captionPath: string[]; }[]) => {
            return position[0].captionPath[1];
        });

        const selectElement = list.map((element: string) => {
            return (
                <Select.Option value={element} label={element}>
                    {element}
                </Select.Option>
            )
        });

        setPortfolioOptions(selectElement)
    }



    const optimizePortfolio = async () => {
        const iter_token = selectedIteration.split("|");
        const payload = {
            "portfolio": selectedPortfolio,
            "iteration": iter_token[0],
            "method": iter_token[1]
        };

        await axios
            .post(`${apUrl}/optimize`, payload)
            .then(response => {
                message.success(`Optimization of portfolio ${selectedPortfolio} from ${selectedIteration} completed.`);
                console.log("Response", response);
            })
            .catch(err => {
                message.error(`Error encountered during uploading portfolio optimization.`);
            });
    };

    return (
        <div ref={container} style={{ padding: '20px', height: "100%", width: "100%" }}>
            <Select
                id="portfolioSelect"
                style={selectStyles}
                showSearch
                optionLabelProp="label"
                listHeight={window.innerHeight - 400}
                placeholder="Select portfolio"
                value={selectedPortfolio}
                onChange={(value) => { setSelectedPortfolio(value); setDisableIteration(false); }}
            >
                {portfolioOptions}
            </Select>
            <Select
                id="iterationSelect"
                style={{ width: 250, paddingLeft: "5px", paddingRight: "5px" }}
                showSearch
                optionLabelProp="label"
                listHeight={window.innerHeight - 400}
                placeholder="Select iteration"
                disabled={disableIteration}
                value={selectedIteration}
                onClick={updateIteration}
                onChange={(value) => { setSelectedIteration(value); }}
            >
                {iterationOptions}
            </Select>
            <Button type="primary" shape="round" disabled={disableIteration} icon={<SettingOutlined />} onClick={() => optimizePortfolio()} />
        </div>

    );
};
