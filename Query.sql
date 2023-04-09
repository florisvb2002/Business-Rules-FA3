# Content Filtering SQL query

CREATE TABLE meest_gekocht (id SERIAL NOT NULL, category varchar(255), profileid varchar(255), productid varchar(255) NOT NULL, PRIMARY KEY (id));
ALTER TABLE meest_gekocht ADD CONSTRAINT FKmeest_geko556806 FOREIGN KEY (productid) REFERENCES product (id);
ALTER TABLE meest_gekocht ADD CONSTRAINT FKmeest_geko34921 FOREIGN KEY (profileid) REFERENCES profile (id);

# Collab Filtering SQL query

CREATE TABLE populaire_producten (id SERIAL NOT NULL, category varchar(255), productid varchar(255) NOT NULL);
