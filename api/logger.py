from loguru import logger

logger.add("./log/chaoxing.log", rotation="10 MB", level="TRACE")