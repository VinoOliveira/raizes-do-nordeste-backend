import enum


class Perfil(str, enum.Enum):
    CLIENTE = "CLIENTE"
    ATENDENTE = "ATENDENTE"
    COZINHA = "COZINHA"
    GERENTE = "GERENTE"


class CanalPedido(str, enum.Enum):
    APP = "APP"
    TOTEM = "TOTEM"
    BALCAO = "BALCAO"
    PICKUP = "PICKUP"
    WEB = "WEB"


class StatusPedido(str, enum.Enum):
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


# cozinha -> pronto -> entregue; cancelamento permitido antes da entrega
TRANSICOES_STATUS_VALIDAS = {
    StatusPedido.AGUARDANDO_PAGAMENTO: {StatusPedido.EM_PREPARO, StatusPedido.CANCELADO},
    StatusPedido.EM_PREPARO: {StatusPedido.PRONTO, StatusPedido.CANCELADO},
    StatusPedido.PRONTO: {StatusPedido.ENTREGUE, StatusPedido.CANCELADO},
    StatusPedido.ENTREGUE: set(),
    StatusPedido.CANCELADO: set(),
}


class FormaPagamento(str, enum.Enum):
    MOCK = "MOCK"
    PIX = "PIX"
    CARTAO = "CARTAO"


class StatusPagamento(str, enum.Enum):
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"
    PENDENTE = "PENDENTE"


class TipoMovimentoEstoque(str, enum.Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"


class TipoTransacaoFidelidade(str, enum.Enum):
    GANHO = "GANHO"
    RESGATE = "RESGATE"
