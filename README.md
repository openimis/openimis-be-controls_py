# openIMIS Backend controls reference module

This repository holds the files of the OpenIMIS Backend Controls reference module.
It is dedicated to be deployed as a module of [openimis-be_py](https://github.com/openimis/openimis-be_py).

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)


## ORM mapping:

| Database table name | Django Model |
| - | - |
| `tblControls` | `Control` |

## Listened Django Signals

None

## Services

None

## Reports (template can be overloaded via report.ReportDefinition)

None

## GraphQL Queries

* `control`
* `control_str`: full text search on Control name, usage, and adjustability

## GraphQL Mutations - each mutation emits default signals and return standard error lists (cfr. openimis-be-core_py)

None

## Configuration options (can be changed via core.ModuleConfiguration)

None

## openIMIS Modules Dependencies

None