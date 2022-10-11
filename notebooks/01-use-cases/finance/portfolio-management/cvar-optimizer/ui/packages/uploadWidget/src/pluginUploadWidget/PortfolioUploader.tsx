import React, { FC, useState, useRef } from "react";
import { useActivePivotClient, useDataModels, WidgetPluginProps } from "@activeviam/activeui-sdk";
import { Upload, Button, message } from 'antd';
import type { UploadProps } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import axios from "axios";
import papa from "papaparse";

export const PortfolioUploader: FC<WidgetPluginProps> = (props) => {
    const container = useRef<HTMLDivElement>(null);
    // const [selectedFile, setSelectedFile] = useState<any>();
    // const [selectedFileList, setSelectedFileList] = useState<any>();
    const [selectedFile, setSelectedFile] = useState<any>();
    
    const dataModels = useDataModels();

    if (Object.keys(dataModels).length !== 1) {
      return (<div>Not implemented for multiple servers yet.</div>)
    };
    const serverKey = Object.keys(dataModels)[0];
    const apClient = useActivePivotClient(serverKey);
    const apUrl = `${apClient.url}/atoti/pyapi`;
    
    const uploadPortfolio: UploadProps['customRequest'] = async ({ onSuccess, onError }) => {

        papa.parse(selectedFile, {
            complete: async (results) => {
                console.log("Finished:", results.data);
                axios
                    .post(`${apUrl}/upload/portfolio`, { portfolio: results.data })
                    .then(response => {
                        onSuccess?.("OK", response.request);
                        message.success("Portfolio(s) uploaded successfully.");
                        console.log("Response", response);
                    })
                    .catch(err => {
                        const error = new Error('Some error');
                        onError?.(error, err);
                        message.error(`Error encountered during uploading of portfolio(s).`);
                    });
            }
        });

    }

    const beforeUpload = (file) => {
        setSelectedFile(file);
        return true;
    }

    const uploadProps: UploadProps = {
        beforeUpload: beforeUpload,
        multiple: false,
        customRequest: uploadPortfolio
    };

    return (
        <div ref={container} style={{ padding: '20px', height: "100%", width: "100%" }}>
            <Upload {...uploadProps} accept=".csv" >
                <Button icon={<UploadOutlined />} type="primary">Upload</Button>
            </Upload>
        </div>
    );
};
