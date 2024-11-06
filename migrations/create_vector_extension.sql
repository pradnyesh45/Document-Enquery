-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a custom operator class for vector similarity search
CREATE OPERATOR CLASS vector_cosine_ops
    FOR TYPE vector
    USING ivfflat
    AS
    OPERATOR 1 <-> (vector, vector) FOR ORDER BY float_ops; 