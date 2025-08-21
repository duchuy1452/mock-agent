-- Create database tables for Expert Sure system

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    auto_mode BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'initialized',
    data_source_path TEXT,
    schema_path TEXT,
    template_path TEXT,
    available_fields JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Slides table
CREATE TABLE slides (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    slide_number INTEGER NOT NULL,
    slide_title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    agent_selected_fields JSONB,
    user_modified_fields JSONB,
    final_fields JSONB,
    analysis_result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, slide_number)
);

-- Project outputs table
CREATE TABLE project_outputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    output_type VARCHAR(50) NOT NULL,
    file_path TEXT,
    content JSONB,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- WebSocket sessions table
CREATE TABLE websocket_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    disconnected_at TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_slides_project_id ON slides(project_id);
CREATE INDEX idx_slides_status ON slides(status);
CREATE INDEX idx_project_outputs_project_id ON project_outputs(project_id);
CREATE INDEX idx_websocket_sessions_project_id ON websocket_sessions(project_id);
CREATE INDEX idx_websocket_sessions_active ON websocket_sessions(is_active);

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updating updated_at
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_slides_updated_at BEFORE UPDATE ON slides 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 