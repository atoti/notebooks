import atoti as tt


class Tables:
    """
    This class creates the tables and setup the table relationship required for the IRRBB trade cube on initiation:
    - TradeBase
    - TradeAttributes
    - IRDelta
    - IRVega
    - SIDelta
    - NMR Cashflow
    - Historical Risk Factor
    - Historical Dates
    - Portfolio

    It also allows for the enhancement of the Capital Charge cube with the following tables:
    - Optionality Charge
    - Historical ICC
    - OtherAPRAAmount

    Args:
        session: The Atoti session
    """

    def __init__(self, session):
        self.session = session
        self.setup_trade_tables()

    def setup_trade_tables(self):
        """
        This function creates the tables for the trade cube:
            - TradeBase
            - TradeAttributes
            - IRDelta
            - IRVega
            - SIDelta
            - NMR Cashflow
            - Historical Risk Factor
            - Historical Dates
            - Portfolio
        """
        self.tradeBaseTbl = self.session.create_table(
            name="TradeBase",
            types={
                "InternalKey": tt.type.STRING,
                "CashflowKey": tt.type.STRING,
                "AsOfDate": tt.type.LOCAL_DATE,
                "TradeID": tt.type.STRING,
                "RiskFactor": tt.type.STRING,
                "RiskFactorType": tt.type.STRING,
                "RiskMeasure": tt.type.STRING,
            },
            keys=["InternalKey", "CashflowKey"],
            default_values={"CashflowKey": "-"},
        )

        self.tradeAttributeTbl = self.session.create_table(
            name="TradeAttributes",
            types={
                "InternalKey": tt.type.STRING,
                "AsOfDate": tt.type.LOCAL_DATE,
                "ItemType": tt.type.STRING,
                "ProductType": tt.type.STRING,
                "Book": tt.type.STRING,
                "LegalEntity": tt.type.STRING,
                "SourceSystem": tt.type.STRING,
                "Notional": tt.type.LONG,
                "NotionalCcy": tt.type.STRING,
                "EconomicValue": tt.type.LONG,
                "EconomicValueCcy": tt.type.STRING,
                "Counterparty": tt.type.STRING,
                "IssueDate": tt.type.LOCAL_DATE,
                "TradeDate": tt.type.LOCAL_DATE,
                "MaturityDate": tt.type.LOCAL_DATE,
                "NextRepriceDate": tt.type.LOCAL_DATE,
                "NextPaymentDate": tt.type.LOCAL_DATE,
                "Compounding Frequency": tt.type.DOUBLE,
                "FixingType": tt.type.STRING,
                "RepaymentFrequency": tt.type.DOUBLE,
            },
            keys=["InternalKey"],
        )

        self.irDeltaTbl = self.session.create_table(
            name="IRDelta",
            types={
                "InternalKey": tt.type.STRING,
                "DeltaCcy": tt.type.STRING,
                "DeltaSensitivities": tt.type.DOUBLE_ARRAY,
            },
            keys=["InternalKey"],
        )

        self.irVegaTbl = self.session.create_table(
            name="IRVega",
            types={
                "InternalKey": tt.type.STRING,
                "VegaCcy": tt.type.STRING,
                "VegaSensitivities": tt.type.DOUBLE_ARRAY,
            },
            keys=["InternalKey"],
        )

        self.siDeltaTbl = self.session.create_table(
            name="SIDelta",
            types={
                "InternalKey": tt.type.STRING,
                "SIDeltaCcy": tt.type.STRING,
                "SIDeltaSensitivities": tt.type.DOUBLE_ARRAY,
            },
            keys=["InternalKey"],
        )

        self.nmrCashFlowTbl = self.session.create_table(
            name="NMR Cashflow",
            types={
                "InternalKey": tt.type.STRING,
                "CashflowKey": tt.type.STRING,
                "CashFlowCcy": tt.type.STRING,
                "CashFlowValues": tt.type.DOUBLE_ARRAY,
                "CashFlowType": tt.type.STRING,
                "BehaviourOptionalityStressedCF": tt.type.STRING,
                "BehaviourOptionType": tt.type.STRING,
                "BehaviourOption": tt.type.STRING,
            },
            keys=["InternalKey", "CashflowKey"],
        )

        self.historicalRFTbl = self.session.create_table(
            name="Historical Risk Factor",
            types={
                "AsOfDate": tt.type.LOCAL_DATE,
                "RiskFactor": tt.type.STRING,
                "Tenor": tt.type.INT,
                "RFValue": tt.type.DOUBLE_ARRAY,
                "PrevRFValue": tt.type.DOUBLE_ARRAY,
            },
            keys=["AsOfDate", "RiskFactor", "Tenor"],
        )

        self.historicalDateTbl = self.session.create_table(
            name="Historical Dates",
            types={
                "AsOfDate": tt.type.LOCAL_DATE,
                "HistoricalDate": tt.type.LOCAL_DATE,
                "HistoricalDateIndex": tt.type.INT,
            },
            keys=["AsOfDate", "HistoricalDate"],
        )

        self.portfolioTbl = self.session.create_table(
            name="Portfolio",
            types={
                "AsOfDate": tt.type.LOCAL_DATE,
                "GroupLevel": tt.type.STRING,
                "ParentBook": tt.type.STRING,
                "SubParentBook": tt.type.STRING,
                "Book": tt.type.STRING,
                "Account": tt.type.STRING,
                "LegalEntity": tt.type.STRING,
                "BalanceSheetCategory": tt.type.STRING,
                "AccrualBasis": tt.type.STRING,
                "ParentLegalEntity": tt.type.STRING,
                "Country": tt.type.STRING,
                "IRRBBDesk": tt.type.STRING,
            },
            keys=["AsOfDate", "Book", "LegalEntity"],
        )

        self.tenorsTbl = self.session.create_table(
            name="Tenors",
            types={
                "AsOfDate": tt.type.LOCAL_DATE,
                "RiskFactor": tt.type.STRING,
                "Tenor": tt.type.INT,
                "TenorIndex": tt.type.INT,
                "TenorName": tt.type.STRING,
            },
            keys=["AsOfDate", "RiskFactor", "Tenor"],
        )

        self.setup_trade_schema()

    def setup_trade_schema(self):
        """
        This function sets up the relationship between the tables for trade cube:
        """
        self.tradeBaseTbl.join(
            self.tradeAttributeTbl,
            (self.tradeBaseTbl["InternalKey"] == self.tradeAttributeTbl["InternalKey"])
            & (self.tradeBaseTbl["AsOfDate"] == self.tradeAttributeTbl["AsOfDate"]),
        )
        self.tradeBaseTbl.join(self.irDeltaTbl)
        self.tradeBaseTbl.join(self.siDeltaTbl)
        self.tradeBaseTbl.join(self.irVegaTbl)
        self.tradeBaseTbl.join(self.nmrCashFlowTbl)
        self.tradeBaseTbl.join(self.tenorsTbl)
        self.tradeBaseTbl.join(self.historicalDateTbl)
        self.tenorsTbl.join(self.historicalRFTbl)

        self.tradeAttributeTbl.join(self.portfolioTbl)

    def setup_capitalCharge_cube(self):
        """
        This class creates the tables required for the Capital Charge cube:
        - Optionality Charge
        - Historical ICC
        - OtherAPRAAmount
        """
        self.es_tbl = self.session.tables["Expected Shortfall"]

        self.optionalityChargeTbl = self.session.create_table(
            name="Optionality Charge",
            types={
                "AsOfDate": tt.type.LOCAL_DATE,
                "OCCcalculationDate": tt.type.LOCAL_DATE,
                "OCCValue": tt.type.DOUBLE,
            },
            keys=["AsOfDate", "OCCcalculationDate"],
        )

        self.historcialICCTbl = self.session.create_table(
            name="Historical ICC",
            types={
                "AsOfDate": tt.type.LOCAL_DATE,
                "ICCcalculationDate": tt.type.LOCAL_DATE,
                "ICCValue": tt.type.DOUBLE,
                "1PeriodLastICCValue": tt.type.DOUBLE,
                "2PeriodLastICCValue": tt.type.DOUBLE,
                "3PeriodLastICCValue": tt.type.DOUBLE,
                "AvgLast3ICC": tt.type.DOUBLE,
            },
            keys=["AsOfDate", "ICCcalculationDate"],
        )

        self.otherAPRAAmtTbl = self.session.create_table(
            name="OtherAPRAAmount",
            types={
                "AsOfDate": tt.type.LOCAL_DATE,
                "OAAcalculationDate": tt.type.LOCAL_DATE,
                "OAAValue": tt.type.DOUBLE,
            },
            keys=["AsOfDate", "OAAcalculationDate"],
        )

        self.setup_capitalCharge_schema()

    def setup_capitalCharge_schema(self):
        """
        This function sets up the relationship between the tables for Capital charge cube:
        """
        self.es_tbl.join(self.optionalityChargeTbl)
        self.es_tbl.join(self.historcialICCTbl)
        self.es_tbl.join(self.otherAPRAAmtTbl)
