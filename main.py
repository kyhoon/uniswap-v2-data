import argparse
import logging
from alive_progress import alive_bar
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError
from gql.transport.requests import log as requests_logger
from pony import orm

from queries import query_pairs_init, query_pairs
from queries import query_transactions_init, query_transactions
from models import init_db
from models import Token, Pair, PairSnapshot
from models import Transaction, Mint, Burn, Swap

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
requests_logger.setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
transport = RequestsHTTPTransport(url=url)
client = Client(transport=transport, fetch_schema_from_transport=True)


@orm.db_session
def get_token(data):
    token_id = str(data["id"])
    token = Token.get(id=token_id)
    if token is None:
        token = Token(
            id=token_id,
            symbol=data["symbol"],
            name=data["name"],
        )
        orm.commit()
    return token


@orm.db_session
def get_pair(data):
    pair_id = str(data["id"])
    pair = Pair.get(id=pair_id)
    if pair is None:
        token0 = get_token(data["token0"])
        token1 = get_token(data["token1"])
        pair = Pair(
            id=pair_id,
            token0=token0,
            token1=token1,
        )
        orm.commit()
    return pair


def get_pair_snapshots(from_block, to_block):
    # get the total number of snapshots
    total = 0
    skip_id = ""
    while True:
        query = query_pairs_init(skip_id, from_block, to_block)
        try:
            response = client.execute(query)
        except TransportQueryError as e:
            logger.error(e)
            continue
        data = response.get("pairs", [])
        if len(data) == 0:
            break

        total += len(data)
        skip_id = data[-1]["id"]
    logger.info(f"total number of pair snapshots: {total}")

    # crawl snapshot data
    with alive_bar(manual=True) as bar:
        count = 0
        skip_id = ""
        while True:
            query = query_pairs(skip_id, from_block, to_block)
            try:
                response = client.execute(query)
            except TransportQueryError as e:
                logger.error(e)
                continue
            data = response.get("pairs", [])
            if len(data) == 0:
                break

            logger.debug(f"fetching pair snapshots {data[0]['id']}")
            for _data in data:
                with orm.db_session:
                    snapshot_id = str(_data["id"]) + str(_data["createdAtBlockNumber"])
                    snapshot = PairSnapshot.get(id=snapshot_id)
                    if snapshot is None:
                        snapshot = PairSnapshot(
                            id=snapshot_id,
                            pair=get_pair(_data),
                            token0Price=_data["token0Price"],
                            token1Price=_data["token1Price"],
                            reserve0=_data["reserve0"],
                            reserve1=_data["reserve1"],
                            totalSupply=_data["totalSupply"],
                            reserveETH=_data["reserveETH"],
                            reserveUSD=_data["reserveUSD"],
                            trackedReserveETH=_data["trackedReserveETH"],
                            volumeToken0=_data["volumeToken0"],
                            volumeToken1=_data["volumeToken1"],
                            volumeUSD=_data["volumeUSD"],
                            untrackedVolumeUSD=_data["untrackedVolumeUSD"],
                            txCount=_data["txCount"],
                            createdAtTimestamp=_data["createdAtTimestamp"],
                            createdAtBlockNumber=_data["createdAtBlockNumber"],
                            liquidityProviderCount=_data["liquidityProviderCount"],
                        )
                    orm.commit()

            count += len(data)
            skip_id = data[-1]["id"]
            bar(count / total)


def get_transactions(from_block, to_block):
    # get the total number of transactions
    total = 0
    skip_id = ""
    while True:
        query = query_transactions_init(skip_id, from_block, to_block)
        try:
            response = client.execute(query)
        except TransportQueryError as e:
            logger.error(e)
            continue
        data = response.get("transactions", [])
        if len(data) == 0:
            break

        total += len(data)
        skip_id = data[-1]["id"]
    logger.info(f"total number of transactions: {total}")

    # crawl transaction data
    with alive_bar(manual=True) as bar:
        skip_id = ""
        count = 0
        while True:
            query = query_transactions(skip_id, from_block, to_block)
            try:
                response = client.execute(query)
            except TransportQueryError as e:
                logger.error(e)
                continue
            data = response.get("transactions", [])
            if len(data) == 0:
                break

            logger.debug(f"fetching transactions {data[0]['id']}")
            for _data in data:
                with orm.db_session:
                    tx_id = str(_data["id"])
                    tx = Transaction.get(id=tx_id)
                    if tx is None:
                        tx = Transaction(
                            id=tx_id,
                            blockNumber=_data["blockNumber"],
                            timestamp=_data["timestamp"],
                        )

                    mints = []
                    for _mint in _data["mints"]:
                        mint_id = str(_mint["id"])
                        mint = Mint.get(id=mint_id)
                        if mint is None:
                            mint = Mint(
                                id=mint_id,
                                transaction=tx,
                                timestamp=_mint["timestamp"],
                                pair=get_pair(_mint["pair"]),
                                sender=_mint["sender"],
                                to=_mint["to"],
                                feeTo=_mint["feeTo"],
                                liquidity=_mint["liquidity"],
                                feeLiquidity=_mint["feeLiquidity"],
                                amount0=_mint["amount0"],
                                amount1=_mint["amount1"],
                                amountUSD=_mint["amountUSD"],
                                logIndex=_mint["logIndex"],
                            )
                        mints.append(mint)

                    burns = []
                    for _burn in _data["burns"]:
                        burn_id = str(_burn["id"])
                        burn = Burn.get(id=burn_id)
                        if burn is None:
                            burn = Burn(
                                id=burn_id,
                                transaction=tx,
                                timestamp=_burn["timestamp"],
                                pair=get_pair(_burn["pair"]),
                                sender=_burn["sender"],
                                to=_burn["to"],
                                feeTo=_burn["feeTo"],
                                liquidity=_burn["liquidity"],
                                feeLiquidity=_burn["feeLiquidity"],
                                amount0=_burn["amount0"],
                                amount1=_burn["amount1"],
                                amountUSD=_burn["amountUSD"],
                                needsComplete=_burn["needsComplete"],
                                logIndex=_burn["logIndex"],
                            )
                        burns.append(burn)

                    swaps = []
                    for _swap in _data["swaps"]:
                        swap_id = str(_swap["id"])
                        swap = Swap.get(id=swap_id)
                        if swap is None:
                            swap = Swap(
                                id=swap_id,
                                transaction=tx,
                                timestamp=_swap["timestamp"],
                                pair=get_pair(_swap["pair"]),
                                sender=_swap["sender"],
                                to=_swap["to"],
                                amount0In=_swap["amount0In"],
                                amount1In=_swap["amount1In"],
                                amount0Out=_swap["amount0Out"],
                                amount1Out=_swap["amount1Out"],
                                amountUSD=_swap["amountUSD"],
                                logIndex=_swap["logIndex"],
                            )
                        swaps.append(swap)

                    orm.commit()

            count += len(data)
            skip_id = data[-1]["id"]
            bar(count / total)


def main(args):
    get_pair_snapshots(args.from_block, args.to_block)
    get_transactions(args.from_block, args.to_block)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database",
        type=str,
        default="./database.sqlite",
        help="path for the SQLite database file",
    )
    parser.add_argument(
        "--from_block",
        type=int,
        default=14960000,
        help="blocknumber of the first block to crawl",
    )
    parser.add_argument(
        "--to_block",
        type=int,
        default=14968000,
        help="blocknumber of the last block to crawl",
    )
    args = parser.parse_args()

    logger.info("initializing SQLite database")
    init_db(args)

    logger.info(
        f"begin crawling Uniswap V2 data from block {args.from_block} to {args.to_block}"
    )
    main(args)
