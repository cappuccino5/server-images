#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    create role test with login password 'test-password';
    create database test with owner test;
EOSQL