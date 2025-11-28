CORES = {
    "vermelho": "\033[31m",
    "verde": "\033[32m",
    "verde_neon" : "\033[38;5;46m",
    "amarelo": "\033[33m",
    "amarelo_claro" :"\033[93m", 
    "azul": "\033[34m",
    "azul_claro" : "\033[94m", 
    "reset": "\033[0m",
    "ciano" : '\033[36m',
    "ciano_claro" : "\033[96m",
    "ciano_neon" : "\033[38;5;51m",
    "ram" : "\033[95m",
    "barramento": "\033[94m",
    "processador": "\033[95m",
    "cache": "\033[90m"
}

def color(texto: str, cor: str) -> str:
    return f"{CORES.get(cor, CORES['reset'])}{texto}{CORES['reset']}"

__all__ = ["color"]