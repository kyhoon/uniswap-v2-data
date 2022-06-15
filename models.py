from pony.orm import Database, PrimaryKey, Set
from pony.orm import Required, Optional

db = Database()


class Token(db.Entity):
    id = PrimaryKey(str, auto=False)
    symbol = Required(str)
    name = Optional(str, nullable=True)

    pairs0 = Set("Pair", reverse="token0")
    pairs1 = Set("Pair", reverse="token1")


class Pair(db.Entity):
    id = PrimaryKey(str, auto=False)
    token0 = Required(Token)
    token1 = Required(Token)

    snapshots = Set("PairSnapshot")
    mints = Set("Mint")
    burns = Set("Burn")
    swaps = Set("Swap")


class PairSnapshot(db.Entity):
    id = PrimaryKey(str, auto=False)
    pair = Required(Pair)

    token0Price = Required(str)
    token1Price = Required(str)

    reserve0 = Required(str)
    reserve1 = Required(str)
    totalSupply = Required(str)
    reserveETH = Required(str)
    reserveUSD = Required(str)
    trackedReserveETH = Required(str)

    volumeToken0 = Required(str)
    volumeToken1 = Required(str)
    volumeUSD = Required(str)
    untrackedVolumeUSD = Required(str)

    txCount = Required(int)
    createdAtTimestamp = Required(int)
    createdAtBlockNumber = Required(int)
    liquidityProviderCount = Required(int)


class Transaction(db.Entity):
    id = PrimaryKey(str, auto=False)
    blockNumber = Required(int)
    timestamp = Required(int)

    mints = Set("Mint")
    burns = Set("Burn")
    swaps = Set("Swap")


class Mint(db.Entity):
    id = PrimaryKey(str, auto=False)
    transaction = Required(Transaction)
    timestamp = Required(int)

    pair = Required(Pair)
    sender = Required(str)
    to = Required(str)
    feeTo = Optional(str, nullable=True)
    liquidity = Required(str)
    feeLiquidity = Optional(str, nullable=True)

    amount0 = Required(str)
    amount1 = Required(str)
    amountUSD = Required(str)

    logIndex = Required(int)


class Burn(db.Entity):
    id = PrimaryKey(str, auto=False)
    transaction = Required(Transaction)
    timestamp = Required(int)

    pair = Required(Pair)
    sender = Required(str)
    to = Required(str)
    feeTo = Optional(str, nullable=True)
    liquidity = Required(str)
    feeLiquidity = Optional(str, nullable=True)

    amount0 = Required(str)
    amount1 = Required(str)
    amountUSD = Required(str)

    needsComplete = Required(bool)
    logIndex = Required(int)


class Swap(db.Entity):
    id = PrimaryKey(str, auto=False)
    transaction = Required(Transaction)
    timestamp = Required(int)

    pair = Required(Pair)
    sender = Required(str)
    to = Required(str)

    amount0In = Required(str)
    amount1In = Required(str)
    amount0Out = Required(str)
    amount1Out = Required(str)
    amountUSD = Required(str)

    logIndex = Required(int)


def init_db(args):
    db.bind(provider="sqlite", filename=args.database, create_db=True)
    db.generate_mapping(create_tables=True)
