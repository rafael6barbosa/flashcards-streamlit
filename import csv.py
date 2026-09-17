import csv

cards = [
    ("Como lidar com desbalanceamento severo de dados (Data Skew) em joins grandes no PySpark?",
     "Identifique as chaves enviesadas e aplique a tecnica de Salting: adicione um sufixo aleatorio (ex: de 0 a N) a chave de join na tabela enviesada e duplique as linhas correspondentes na outra tabela para redistribuir o processamento de forma homogenea entre os executores.",
     "pyspark data-skew performance join optimization"),
    
    ("O que fazer quando ocorre erro de OOM (OutOfMemory) durante operacoes de Shuffle?",
     "Aumente 'spark.sql.shuffle.partitions' (o padrao de 200 pode ser insuficiente para terabytes), aumente 'spark.executor.memoryOverhead' ou otimize as operacoes reduzindo a quantidade de dados trafegados antes do shuffle via filtros precoces e selecao de colunas.",
     "pyspark oom memory shuffle tuning"),
    
    ("Como otimizar a leitura de bilhões de pequenos arquivos no HDFS ou S3 (Small Files Problem)?",
     "Utilize 'spark.read.option(\"maxPartitionBytes\", 134217728)' para agrupar arquivos pequenos na leitura ou consolide a tabela de origem escrevendo dados com '.repartition(N)' ou usando 'coalesce()' para gerar arquivos maiores (ex: 128MB a 512MB).",
     "pyspark small-files s3 hdfs io-optimization"),
    
    ("Qual a diferença entre coalesce() e repartition() no PySpark e quando usar cada um?",
     "repartition() reduz ou aumenta o numero de particoes realizando shuffle completo dos dados; use para reequilibrar a carga. coalesce() apenas reduz o numero de particoes minimizando a movimentacao de dados sem shuffle total; use imediatamente antes de salvar no disco.",
     "pyspark partitioning repartition coalesce performance"),
    
    ("Como evitar o estouro de memória no Driver quando se usa collect() em DataFrames grandes?",
     "Substitua '.collect()' por operacoes de agregacao no proprio cluster ou use '.take(N)' / '.sample()' para inspecionar amostras. Se precisar exportar dados completos use formatos distribuida como Parquet/CSV via '.write'.",
     "pyspark driver oom collect best-practices"),
    
    ("Como aplicar Broadcast Join no PySpark e qual o limite ideal para a tabela menor?",
     "Importe 'broadcast' de 'pyspark.sql.functions' e envolva o DataFrame menor: 'df1.join(broadcast(df2), \"key\")'. O tamanho ideal padrao e ate 10MB (configuravel em 'spark.sql.autoBroadcastJoinThreshold'), evitando shuffle no cluster.",
     "pyspark broadcast-join performance optimization"),
    
    ("Como atualizar/upsertar dados existentes em uma Lakehouse sem reescrever toda a tabela?",
     "Utilize o formato Delta Lake ou Apache Iceberg no PySpark e aplique o comando 'MERGE INTO' (DeltaTable.forName(...).merge(...)), permitindo UPDATE, INSERT e DELETE em lote com acid ACID.",
     "pyspark delta-lake iceberg merge upsert lakehouse"),
    
    ("Como tratar registros duplicados mantendo apenas o registro mais recente com base num timestamp?",
     "Crie uma Window especificada por particao de chave e ordenacao descendente do timestamp. Aplique 'row_number().over(window)' e filtre registros onde 'row_number == 1'.",
     "pyspark window-functions deduplication data-modeling"),
    
    ("Como evitar o erro 'Task Not Serializable' ao usar UDFs no PySpark?",
     "Certifique-se de nao referenciar objetos nao serializaveis (como conexoes de banco ou contextos dentro da UDF). Instancie conexoes dentro das particoes com 'rdd.mapPartitions()' ou utilize Pandas UDFs (PyArrow) de forma vetorizada.",
     "pyspark udf serialization error-handling"),
    
    ("Como otimizar o desempenho de UDFs em Python puro no PySpark?",
     "Substitua UDFs Python padrao por 'Pandas UDFs' (@pandas_udf) com suporte a Apache Arrow, ou preferencialmente use as funcoes nativas de 'pyspark.sql.functions' executadas diretamente na JVM.",
     "pyspark pandas-udf pyarrow performance"),
    
    ("Como garantir a idempotência em pipelines de ingestão incremental no PySpark?",
     "Escreva dados utilizando partiçoes dinamicas com mode('overwrite') e a opcao 'partitionOverwriteMode=dynamic', garantindo que apenas as particoes processadas na execucao atual sejam sobrescritas.",
     "pyspark idempotency data-pipeline ingestion"),
    
    ("Como converter colunas do tipo JSON string em colunas estruturadas no PySpark?",
     "Defina um StructType representando o esquema do JSON e utilize a funcao 'from_json(col(\"json_str\"), schema)' para criar colunas complexas acessiveis diretamente por ponto.",
     "pyspark json schema parsing data-modeling"),
    
    ("Como tratar variação dinâmica de esquemas (Schema Evolution) na escrita em Delta Lake?",
     "Adicione a opcao '.option(\"mergeSchema\", \"true\")' no comando '.write.format(\"delta\")' para permitir que novas colunas sejam adicionadas automaticamente a tabela Delta existente.",
     "pyspark delta-lake schema-evolution lakehouse"),
    
    ("O que é Spill to Disk / Spill to Memory e como mitigar no PySpark?",
     "Spill ocorre quando os dados de uma particao excedem a RAM do executor e o Spark grava temporariamente em disco, reduzindo drasticamente a velocidade. Solucao: aumentar memoria por executor, redefinir particionamento ou eliminar skews.",
     "pyspark memory-management spill optimization"),
    
    ("Como ler eficientemente tabelas relacionais JDBC (PostgreSQL/MySQL) de grande porte no PySpark?",
     "Passe os parametros 'partitionColumn', 'lowerBound', 'upperBound' e 'numPartitions' na leitura JDBC para que o Spark crie multiplas conexoes paralelas dividindo a query por faixas de valores de ID.",
     "pyspark jdbc postgresql parallelism ingestion"),
    
    ("Como consultar dados em tempo real usando Structured Streaming no PySpark?",
     "Utilize 'spark.readStream.format(\"kafka\").option(...).load()' seguido por transformacoes e grave o fluxo com 'df.writeStream.format(\"delta\").option(\"checkpointLocation\", path).start()'.",
     "pyspark streaming kafka structured-streaming"),
    
    ("Como evitar o problema de 'out of disk space' por conta de arquivos de log do Spark?",
     "Configure a politica de retencao de logs no cluster, ajuste 'spark.cleaner.periodicGC.interval' e configure 'spark.history.fs.cleaner.enabled=true' para descartar event logs antigos periodicamente.",
     "pyspark devops logging cluster-maintenance"),
    
    ("Como realizar transformações complexas linha a linha sem perder performance de execução?",
     "Utilize 'mapPartitions()' ao invés de 'map()' individual para processar dados em lote por particao, reduzindo o overhead de criacao de objetos e conexoes por elemento.",
     "pyspark mapPartitions performance advanced"),
    
    ("Como acelerar consultas frequentes no PySpark via caching inteligente?",
     "Utilize 'df.persist(StorageLevel.MEMORY_AND_DISK)' em DataFrames reutilizados multiplas vezes no mesmo job e certifique-se de liberar a memoria com 'df.unpersist()' ao terminar.",
     "pyspark caching persist memory-optimization"),
    
    ("Como criar uma coluna com contagem regressiva ou tempo transcorrido entre eventos por cliente?",
     "Utilize funcoes de Janela com 'lag()' ou 'lead()' ordenadas pelo timestamp do cliente: 'col(\"timestamp\").cast(\"long\") - lag(\"timestamp\").over(window).cast(\"long\")'.",
     "pyspark window-functions lag lead feature-engineering"),
    
    ("Como lidar com arquivos corrompidos ou registros inválidos na leitura de arquivos CSV/JSON?",
     "Utilize a opcao '.option(\"mode\", \"PERMISSIVE\")' com '.option(\"columnNameOfCorruptRecord\", \"_corrupt_record\")' para isolar as linhas invalidas sem falhar o pipeline inteiro.",
     "pyspark error-handling data-quality ingestion"),
    
    ("Como converter uma coluna Array com múltiplos elementos em várias linhas individuais?",
     "Utilize a funcao 'explode(col(\"array_col\"))' ou 'explode_outer()' caso deseje preservar registros onde o array e nulo ou vazio.",
     "pyspark explode data-modeling arrays"),
    
    ("Como agregar múltiplos valores de colunas de texto em uma lista por grupo?",
     "Utilize a funcao de agregacao 'collect_list(col(\"nome\"))' para lista com duplicados ou 'collect_set(col(\"nome\"))' para valores unicos agrupados por chave.",
     "pyspark aggregation collect-list data-modeling"),
    
    ("Como implementar controle de qualidade e validação de dados em pipelines PySpark?",
     "Integre a biblioteca Great Expectations ou PyDeequ para definir verificacoes de completude, unicidade e alcance de valores antes de salvar os dados no destino final.",
     "pyspark data-quality deequ validation architecture"),
    
    ("Como mitigar problemas de dependências de bibliotecas Python em clusters distribuídos?",
     "Utilize ambientes virtuais Conda ou pacotes Wheel empacotados enviados via '--archives' ou configure imagens Docker personalizadas para os executores do cluster Spark.",
     "pyspark devops dependencies conda docker"),
    
    ("Como otimizar a escrita de dados particionados por data para evitar criação excessiva de pastas?",
     "Evite particionar por colunas com cardinalidade alta (como hora/minuto ou ID). Particione no maximo por ano/mes/dia e garanta tamanho de arquivo entre 128MB e 1GB por particao.",
     "pyspark partitioning storage-optimization data-modeling"),
    
    ("Como calcular estatísticas de Machine Learning em larga escala no PySpark?",
     "Utilize 'VectorAssembler' de 'pyspark.ml.feature' para consolidar colunas numericas e aplique modelos do pacote 'pyspark.ml' otimizados para execucao distribuida.",
     "pyspark machine-learning vector-assembler ml"),
    
    ("Como tratar colunas de alta cardinalidade em modelos de ML com PySpark?",
     "Utilize 'StringIndexer' seguido de 'FeatureHasher' ou 'OneHotEncoder' em lote para mapear categorias estrategicamente sem estourar a dimensionalidade da matriz.",
     "pyspark feature-engineering ml high-cardinality"),
    
    ("Como ler múltiplos diretórios de arquivos com padrões de nomes de data específicos?",
     "Passe caminhos glob com wildcards na leitura: 'spark.read.parquet(\"s3://bucket/data/year=2026/month=09/*\")' ou utilize lista de caminhos no parametro 'spark.read.parquet([path1, path2])'.",
     "pyspark ingestion wildcards glob storage"),
    
    ("Como fazer Pivot dinamico de linhas para colunas no PySpark?",
     "Utilize 'df.groupBy(\"categoria\").pivot(\"ano\").agg(sum(\"valor\"))'. Para performance otimizada, passe a lista explicita de valores no pivot: '.pivot(\"ano\", [2024, 2025, 2026])'.",
     "pyspark pivot data-transformation aggregation"),
    
    ("Como mascara/criptografar dados sensíveis (PII) durante o pipeline de ETL PySpark?",
     "Utilize a funcao 'sha2(col(\"cpf\"), 256)' para hashing unidirecional ou integre UDFs nativas de criptografia AES 'expr(\"aes_encrypt(cpf, chave)\")'.",
     "pyspark security pii-masking compliance data-engineering"),
    
    ("Como consultar tabelas Hive Metastore diretamente pelo PySpark?",
     "Instancie a SparkSession habilitando o suporte ao Hive com 'SparkSession.builder.enableHiveSupport().getOrCreate()' e execute queries com 'spark.sql(\"SELECT * FROM db.tabela\")'.",
     "pyspark hive metastore sql architecture"),
    
    ("Como verificar o plano de execução de uma consulta no PySpark e identificar bottlenecks?",
     "Execute 'df.explain(extended=True)' ou 'df.explain(mode=\"formatted\")' para analisar as etapas de Logical Plan, Physical Plan, operacoes de Exchange (Shuffle) e Broadcast.",
     "pyspark query-plan debugging execution-plan optimization"),
    
    ("Como realizar leituras e escritas com consistência transactional em armazenamento em nuvem (S3)?",
     "Utilize formatos de tabela modernizados como Delta Lake ou Apache Iceberg com o AWS S3Guard / S3A Committer para evitar discrepancias por inconsistencia eventual de lista no S3.",
     "pyspark s3 delta-lake transactions cloud-storage"),
    
    ("Como monitorar métricas detalhadas de jobs PySpark em tempo real?",
     "Acesse a Spark UI na porta 4040 ou instale escutadores (SparkListener) customizados exportando metricas de JVM, CPU, GC e I/O para o Prometheus/Grafana.",
     "pyspark monitoring spark-ui metrics observability"),
    
    ("Como lidar com colunas nulas em cálculos matemáticos agregados no PySpark?",
     "Operacoes de agregacao nativas (como sum, avg) ignoram automaticamente nulos. Para operacoes entre colunas na mesma linha, utilize 'coalesce(col(\"a\"), lit(0)) + coalesce(col(\"b\"), lit(0))'.",
     "pyspark null-handling aggregation mathematical-ops"),
    
    ("Como carregar um modelo de ML pré-treinado em formato PMML ou ONNX no PySpark?",
     "Utilize bibliotecas de inferencia como 'onnxruntime' dentro de uma 'pandas_udf' para distribuir a predicao do modelo em larga escala em todo o cluster PySpark.",
     "pyspark mlops onnx model-inference ML"),
    
    ("Como otimizar queries com filtros recorrentes usando Z-Ordering no Delta Lake?",
     "Execute o comando OPTIMIZE na tabela Delta com Z-ORDER BY: 'OPTIMIZE tabela ZORDER BY (coluna_filtro1, coluna_filtro2)' para reorganizar dados espacialmente e pular leitura de arquivos inapropriados.",
     "pyspark delta-lake z-ordering optimization performance"),
    
    ("Como fazer parsing de arquivos XML de grande volume no PySpark?",
     "Utilize o pacote externo 'com.databricks:spark-xml' passando o formato '.format(\"xml\")' e a opcao '.option(\"rowTag\", \"tag_raiz\")' para extrair os registros de forma distribuida.",
     "pyspark xml spark-xml data-parsing ingestion"),
    
    ("Como unificar dois DataFrames com esquemas diferentes adicionando colunas ausentes como nulas?",
     "Utilize a opcao 'allowMissingColumns=True' na funcao de uniao por nome: 'df1.unionByName(df2, allowMissingColumns=True)'.",
     "pyspark union dataframe schema-matching"),
    
    ("Como aplicar filtros dinâmicos com base nos resultados de outro DataFrame sem fazer Join tradicional?",
     "Envie a lista de IDs filtrados como Broadcast ou utilize subqueries semi-join com 'df1.filter(col(\"id\").isin(lista_broadcast))' para evitar shuffle de tabelas imensas.",
     "pyspark filtering optimization performance broadcast"),
    
    ("Como realizar limpeza periodica de snapshots e logs antigos no Delta Lake (Vacuum)?",
     "Execute o comando 'deltaTable.vacuum(retain_hours)' com retencao apropriada (padrao 168 horas) para deletar fisicamente arquivos de dados nao mais referenciados no log Delta.",
     "pyspark delta-lake vacuum storage-maintenance cleanup"),
    
    ("Como limitar a taxa de ingestão de dados em Structured Streaming para não sobrecarregar o cluster?",
     "Defina a configuracao '.option(\"maxFilesPerTrigger\", N)' para leitura de arquivos ou '.option(\"maxOffsetsPerTrigger\", N)' para fontes de dados Kafka.",
     "pyspark streaming rate-limiting kafka backpressure"),
    
    ("Como tratar fusos horários e timezone em conversões de string para Timestamp?",
     "Ajuste a sessao do Spark com 'spark.conf.set(\"spark.sql.session.timeZone\", \"UTC\")' e utilize a funcao 'to_timestamp(col(\"dt\"), \"yyyy-MM-dd HH:mm:ss\")' explicitamente.",
     "pyspark timezone timestamp data-cleaning"),
    
    ("Como converter colunas do tipo Struct ou Array de volta para uma string JSON validada?",
     "Utilize a funcao 'to_json(col(\"coluna_estruturada\"))' de 'pyspark.sql.functions' para serializar os campos complexos de volta em formato string JSON.",
     "pyspark json serialization struct data-transform"),
    
    ("Como criar identificadores únicos (IDs primários) determinísticos sem acoplamento de estado?",
     "Utilize a funcao 'md5(concat_ws(\"||\", col(\"col1\"), col(\"col2\")))' ou 'hash()' para criar uma chave surrogate hash com base nas colunas de negocio.",
     "pyspark surrogate-key hash primary-key data-modeling"),
    
    ("Como re-particionar dados gravados no disco com base no tamanho ideal dos arquivos sem depender apenas do número fixo de partições?",
     "Habilite o Auto-Optimize do Delta Lake ou configure 'spark.sql.files.maxPartitionBytes' para ajustar automaticamente a divisao durante tarefas de escrita/leitura.",
     "pyspark delta-lake auto-optimize file-size partition"),
    
    ("Como calcular estatísticas móveis (rolling average / média móvel) em séries temporais?",
     "Defina uma Janela com 'Window.partitionBy(\"id\").orderBy(\"data\").rowsBetween(-N, 0)' e aplique 'avg(col(\"valor\")).over(window)'.",
     "pyspark window-functions time-series rolling-average"),
    
    ("Como ler múltiplos arquivos de uma pasta adicionando o nome do arquivo de origem como coluna no DataFrame?",
     "Utilize a funcao nativa 'input_file_name()': 'df.withColumn(\"arquivo_origem\", input_file_name())' durante o processo de leitura ou transformacao.",
     "pyspark lineage metadata ingestion input_file_name"),
    
    ("Como exportar resultados do PySpark para um único arquivo CSV sem gerar múltiplos arquivos de partição?",
     "Aplique 'df.coalesce(1).write.option(\"header\", \"true\").csv(\"path\")'. Atencao: utilize apenas para volumes de dados pequenos que caibam na memoria de um unico executor.",
     "pyspark export csv coalesce single-file")
]

csv_filename = "pyspark_flashcards_50.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["front", "back", "tags"])
    for front, back, tags in cards:
        writer.writerow([front, back, tags])

print(f"Created CSV with {len(cards)} rows.")