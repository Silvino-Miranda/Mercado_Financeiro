from datetime import datetime


class Report:
    @staticmethod
    def save(order):
        # Obtém a data atual no formato yyyy-mm-dd
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"report_{date_str}.md"

        # Conteúdo do relatório
        report_content = (
            f"## Relatório de Ordem de Compra\n\n"
            f"- **ID:** {order.order_id}\n"
            f"- **Símbolo:** {order.symbol}\n"
            f"- **Preço:** {order.price}\n"
            f"- **Quantidade:** {order.amount_crypto}\n"
            f"- **Custo:** {order.cost}\n"
        )

        # Escreve o conteúdo em um arquivo .md
        with open("data/" + filename, "w") as file:
            file.write(report_content)

        print(f"Relatório salvo em {filename}")
