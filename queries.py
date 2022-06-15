from gql import gql


def query_pairs_init(skip_id, from_block, to_block):
    return gql(
        f"""
        {{
            pairs (
                first: 1000,
                where: {{
                    id_gt: "{skip_id}"
                    createdAtBlockNumber_gte: {from_block},
                    createdAtBlockNumber_lte: {to_block}
                }}
            ) {{
                id
            }}
        }}
        """
    )


def query_pairs(skip_id, from_block, to_block):
    return gql(
        f"""
        {{
            pairs (
                first: 1000,
                where: {{
                    id_gt: "{skip_id}"
                    createdAtBlockNumber_gte: {from_block},
                    createdAtBlockNumber_lte: {to_block}
                }}
            ) {{
                id
                token0 {{
                    id
                    symbol
                    name
                }}
                token1 {{
                    id
                    symbol
                    name
                }}
                reserve0
                reserve1
                totalSupply
                reserveETH
                reserveUSD
                trackedReserveETH
                token0Price
                token1Price
                volumeToken0
                volumeToken1
                volumeUSD
                untrackedVolumeUSD
                txCount
                createdAtTimestamp
                createdAtBlockNumber
                liquidityProviderCount
            }}
        }}
        """
    )


def query_transactions_init(skip_id, from_block, to_block):
    return gql(
        f"""
        {{
            transactions (
                first: 1000,
                where: {{
                    id_gt: "{skip_id}"
                    blockNumber_gte: {from_block},
                    blockNumber_lte: {to_block}
                }}
            ) {{
                id
            }}
        }}
        """
    )


def query_transactions(skip_id, from_block, to_block):
    return gql(
        f"""
        {{
            transactions (
                first: 1000,
                where: {{
                    id_gt: "{skip_id}"
                    blockNumber_gte: {from_block},
                    blockNumber_lte: {to_block}
                }}
            ) {{
                id
                blockNumber
                timestamp
                mints {{
                    id
                    timestamp
                    pair {{
                        id
                        token0 {{
                            id
                            symbol
                            name
                        }}
                        token1 {{
                            id
                            symbol
                            name
                        }}
                    }}
                    to
                    liquidity
                    sender
                    amount0
                    amount1
                    logIndex
                    amountUSD
                    feeTo
                    feeLiquidity
                }}
                burns {{
                    id
                    timestamp
                    pair {{
                        id
                        token0 {{
                            id
                            symbol
                            name
                        }}
                        token1 {{
                            id
                            symbol
                            name
                        }}
                    }}
                    liquidity
                    to
                    sender
                    amount0
                    amount1
                    logIndex
                    amountUSD
                    feeTo
                    feeLiquidity
                    needsComplete
                }}
                swaps {{
                    id
                    timestamp
                    pair {{
                        id
                        token0 {{
                            id
                            symbol
                            name
                        }}
                        token1 {{
                            id
                            symbol
                            name
                        }}
                    }}
                    to
                    sender
                    amount0In
                    amount1In
                    amount0Out
                    amount1Out
                    logIndex
                    amountUSD
                }}
            }}
        }}
        """
    )
