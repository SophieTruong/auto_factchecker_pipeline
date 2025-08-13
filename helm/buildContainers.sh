cd ../api_service
docker build -t harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/api_service:latest .
docker push harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/api_service:latest
cd ../data_retrieval 
docker build -t harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/data_retrieval:latest .
docker push harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/data_retrieval:latest
cd ../evidence_retrieval
docker build -t harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/evidence_retrieval:latest .
docker push harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/evidence_retrieval:latest
cd ../milvus_standalone
docker build -t harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/db_seed:latest .
docker push harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/db_seed:latest
cd ../model_inference_service
docker build -t harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/model_inference:latest .
docker push harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/model_inference:latest
cd ../model_monitoring_service
docker build -t harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/model_monitoring:latest .
docker build -f app/rabbitmq_consumer/Dockerfile -t harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/rabbitmq_consumer:latest .
docker push harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/model_monitoring:latest
docker push harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/rabbitmq_consumer:latest
cd ../web_scrape
docker build -t harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/web_scrape:latest .
docker push harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/web_scrape:latest
cd ../claim_detection
docker build -t harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/claim_detection:latest .
docker push harbor.cs.aalto.fi/aaltorse-public/auto_fact_check/claim_detection:latest
cd ../helm