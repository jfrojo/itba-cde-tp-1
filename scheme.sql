CREATE TABLE states (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL CHECK (name ~* '[A-Z]{3,}') UNIQUE
);

CREATE TABLE products (
    id BIGINT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL
);

CREATE TABLE issues (
    id BIGINT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL
);

CREATE TABLE companies (
    id BIGINT NOT NULL PRIMARY KEY,
    name TEXT,
    state_id BIGINT NOT NULL REFERENCES states(id),
    zip_code TEXT
);
  
CREATE TABLE complaints (
    id BIGINT NOT NULL PRIMARY KEY,
    reception_date TIMESTAMPTZ,
    product_id BIGINT NOT NULL REFERENCES products(id),
    issue_id BIGINT NOT NULL REFERENCES issues(id),
    company_id BIGINT NOT NULL REFERENCES companies(id),
    tags TEXT,
    consumer_narrative TEXT,
    company_public_response TEXT,
    company_consumer_response TEXT,
    consumer_consent BOOLEAN,
    submission_channel TEXT,
    company_sent_date TIMESTAMPTZ,
    timely_response BOOLEAN,
    consumer_disputed BOOLEAN
);