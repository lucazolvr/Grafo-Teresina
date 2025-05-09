# Grafo-Teresina

Este projeto contém scripts Python para extrair e processar dados de ruas e semáforos de Teresina, Piauí, Brazil, usando o OpenStreetMap (OSM) e a biblioteca OSMnx. Os scripts geram um arquivo JSON com nós (interseções), arestas (vias), e semáforos, que pode ser usado para simulações de tráfego urbano, cálculo de rotas com o algoritmo de Dijkstra, e otimização de semáforos.

## Objetivo

O objetivo é criar uma representação estruturada da rede viária de Teresina, incluindo informações detalhadas sobre interseções, vias, e semáforos, para suportar simulações de tráfego e otimizações em um sistema backend. O projeto é útil para estudos de mobilidade urbana, planejamento de tráfego, e desenvolvimento de algoritmos de roteamento.

## Scripts

O repositório contém dois scripts Python:A

1. **`process_osmnx_map_backward.py`**:
   - Versão inicial do script que extrai dados do OSM para Teresina.
   - Gera um JSON com nós, arestas, e semáforos, mas a inferência de direções dos semáforos (`traffic_signals:direction`) tem um viés para `backward` devido à lógica de priorização de arestas de entrada.
   - Útil para comparação ou cenários onde a direção `backward` é suficiente.

2. **`process_osmnx_map.py`**:
   - Versão aprimorada e recomendada.
   - Inclui uma lógica de inferência de direções mais equilibrada, gerando direções como `forward`, `backward`, `north`, `south`, `east`, `west`, ou `unknown` para os semáforos.
   - Usa informações de arestas `oneway` e coordenadas para determinar direções, compensando a ausência da tag `traffic_signals:direction` no OSM.

Ambos os scripts geram um arquivo JSON na pasta `mapa` (`mapa/CentroTeresinaPiauíBrazil.json`).

## Pré-requisitos

- Python 3.8 ou superior
- Bibliotecas Python:
  - `osmnx`
  - `matplotlib`
  - `geopandas` (dependência do OSMnx)
  - `shapely` (dependência do OSMnx)
  - `numpy` (dependência do OSMnx)

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/lucazolvr/Grafo-Teresina.git
   cd Grafo-Teresina
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install osmnx matplotlib
   ```
   Nota: O OSMnx instalará automaticamente `geopandas`, `shapely`, e `numpy`.

## Como usar

1. **Executar o script desejado**:
   - Para a versão com direções corrigidas:
     ```bash
     python process_osmnx_map.py
     ```
   - Para a versão antiga (viés para `backward`):
     ```bash
     python process_osmnx_map_backward.py
     ```

2. **Saída**:
   - Um arquivo JSON será gerado em `mapa/CentroTeresinaPiauíBrazil.json`.
   - Uma visualização do grafo de ruas será exibida (fechada automaticamente ao continuar).
   - Informações dos semáforos serão impressas no console.

3. **Personalização da região**:
   - Os scripts podem ser usados para extrair dados de outros bairros de Teresina, como Dirceu ou Joquei, ou da cidade inteira. Para isso, altere a variável `place_name` no início do script. Exemplos:
     - Para o bairro Dirceu: `place_name = "Dirceu, Teresina, Piauí, Brazil"`
     - Para o bairro Joquei: `place_name = "Joquei, Teresina, Piauí, Brazil"`
     - Para a cidade inteira: `place_name = "Teresina, Piauí, Brazil"`
   - O arquivo JSON gerado terá o nome ajustado automaticamente com base no `place_name` (ex.: `mapa/DirceuTeresinaPiauíBrazil.json`).

4. **Uso do JSON**:
   - O arquivo JSON pode ser carregado em um backend (ex.: Java/Spring Boot) para:
     - Calcular rotas com Dijkstra usando `nodes` e `edges`.
     - Otimizar semáforos com base em `traffic_lights` (ex.: priorizar direções ou destinos).
   - Veja a seção "Estrutura do JSON" para detalhes dos atributos.

## Estrutura do JSON

O JSON gerado contém três seções principais: `nodes`, `edges`, e `traffic_lights`. Abaixo está a descrição detalhada de cada atributo:

### `nodes`
Representa as interseções ou pontos da rede viária.
- **`id`**: Identificador único do nó (string), extraído do OSM.
- **`latitude`**: Coordenada latitudinal do nó (float), em graus.
- **`longitude`**: Coordenada longitudinal do nó (float), em graus.
- **Uso**: Define os pontos do grafo para cálculo de rotas e mapeamento geográfico.

### `edges`
Representa as vias que conectam os nós.
- **`id`**: Identificador único da aresta (string), no formato `source-target-key`.
- **`source`**: ID do nó de origem da aresta (string).
- **`target`**: ID do nó de destino da aresta (string).
- **`length`**: Comprimento da via em metros (float), usado para calcular distâncias.
- **`travel_time`**: Tempo de viagem em segundos (float), inicialmente 0.0 (pode ser calculado no backend com base em `length` e `maxspeed`).
- **`oneway`**: Indica se a via é de mão única (boolean, `true` para mão única, `false` para bidirecional).
- **`maxspeed`**: Velocidade máxima da via em km/h (float), assume 50 km/h se não disponível no OSM.
- **Uso**: Fornece a estrutura do grafo para algoritmos de roteamento (ex.: Dijkstra) e análise de tráfego.

### `traffic_lights`
Representa os semáforos nos cruzamentos.
- **`id`**: Identificador único do semáforo (string), geralmente o ID do nó correspondente.
- **`latitude`**: Coordenada latitudinal do semáforo (float).
- **`longitude`**: Coordenada longitudinal do semáforo (float).
- **`attributes`**:
  - **`highway`**: Tipo do nó (string), sempre `traffic_signals` para semáforos.
  - **`destination`**: Destino indicado pelo semáforo (string ou `null`), como "downtown" ou "airport", útil para priorizar rotas.
  - **`ref`**: Referência do semáforo (string ou `null`), como um código identificador (ex.: "TS001").
  - **`traffic_signals:direction`**: Direção do fluxo controlado pelo semáforo (string), pode ser `forward`, `backward`, `north`, `south`, `east`, `west`, ou `unknown`. Inferida com base em arestas `oneway` e coordenadas, já que o OSM para Teresina não fornece essa tag.
- **Uso**: Permite modelar atrasos em cruzamentos, priorizar tempos de verde, e otimizar fluxos de tráfego.

### Exemplo de JSON
```json
{
  "nodes": [
    {"id": "123", "latitude": -5.089, "longitude": -42.801},
    ...
  ],
  "edges": [
    {"id": "123-456-0", "source": "123", "target": "456", "length": 100.0, "travel_time": 0.0, "oneway": false, "maxspeed": 50.0},
    ...
  ],
  "traffic_lights": [
    {
      "id": "1524484929",
      "latitude": -5.0812959,
      "longitude": -42.8106077,
      "attributes": {
        "highway": "traffic_signals",
        "destination": null,
        "ref": null,
        "traffic_signals:direction": "north"
      }
    },
    ...
  ]
}
```

## Estrutura dos scripts

### `process_osmnx_map.py`
- **Funcionalidades**:
  - Extrai o grafo de ruas de Teresina usando OSMnx.
  - Gera JSON com nós, arestas, e semáforos.
  - Infere direções dos semáforos (`forward`, `backward`, `north`, `south`, `east`, `west`, `unknown`) com base em arestas `oneway` e coordenadas.
  - Salva o JSON em `mapa/CentroTeresinaPiauíBrazil.json`.
  - Exibe uma visualização do grafo (amarelo, com nós pequenos).
- **Vantagens**:
  - Direções de semáforos mais variadas e precisas.
  - Ideal para simulações complexas de tráfego.

### `process_osmnx_map_backward.py`
- **Funcionalidades**:
  - Similar ao script principal, mas com uma lógica de inferência de direções que favorece `backward`.
  - Útil para testes comparativos ou cenários específicos.
- **Limitações**:
  - Menos preciso devido ao viés para `backward`.

## Notas

- **Dados do OSM**:
  - Os dados são extraídos do OpenStreetMap, que pode ter informações incompletas para Teresina (ex.: ausência de `traffic_signals:direction`, `destination`, ou `ref`). O script principal contorna isso com inferência de direções.
  - Se você tiver dados locais (ex.: da prefeitura), pode integrá-los ao JSON.

- **Limitações**:
  - A inferência de direções é uma aproximação e pode não ser 100% precisa em cruzamentos complexos.
  - O script assume `maxspeed=50 km/h` quando o dado não está disponível.
  - O atributo `travel_time` é inicializado como 0.0 e deve ser calculado no backend.

- **Futuras melhorias**:
  - Integrar dados externos de tráfego.
  - Refinar a inferência de direções para cruzamentos com múltiplas vias.

## Contribuição

Contribuições são bem-vindas! Para contribuir:
1. Faça um fork do repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`).
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`).
4. Push para a branch (`git push origin feature/nova-funcionalidade`).
5. Abra um Pull Request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Contato

Para dúvidas ou sugestões, abra uma issue no GitHub ou entre em contato com [lucas.lima@somosicev.com](mailto:lucas.lima@somosicev.com).
