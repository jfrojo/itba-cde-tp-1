CREATE TABLE states (
    id SERIAL PRIMARY KEY,
    name TEXT CHECK (name ~* '[A-Z]*') UNIQUE
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    type TEXT,

    UNIQUE(name, type)
);

CREATE TABLE issues (
    id SERIAL PRIMARY KEY,
    name TEXT,
    type TEXT,

    UNIQUE(name, type)
);

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    state_id BIGINT NOT NULL REFERENCES states(id),
    zip_code TEXT,

    UNIQUE(name, state_id, zip_code)
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