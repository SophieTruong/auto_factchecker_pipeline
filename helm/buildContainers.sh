cd ../api_service
docker build -t harbor.cs.aalto.fi/aaltorse-public/api_service:latest .
cd ../data_retrieval 
docker build -t harbor.cs.aalto.fi/aaltorse-public/data_retrieval:latest .
cd ../evidence_retrieval
docker build -t harbor.cs.aalto.fi/aaltorse-public/evidence_retrieval:latest .
cd ../milvus_standalone
docker build -t harbor.cs.aalto.fi/aaltorse-public/db_seed:latest .
cd ../model_inference_service
docker build -t harbor.cs.aalto.fi/aaltorse-public/model_inference:latest .
cd ../model_monitoring_service
docker build -t harbor.cs.aalto.fi/aaltorse-public/model_monitoring:latest .
docker build -f app/rabbitmq_consumer/Dockerfile -t harbor.cs.aalto.fi/aaltorse-public/rabbitmq_consumer:latest .
cd ../../web_scrape
docker build -t harbor.cs.aalto.fi/aaltorse-public/web_scrape:latest .
cd ../helm