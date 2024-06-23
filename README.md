# jmeter_perfmon_correlator
A simple Python application to correlate JMeter results with Windows Performance Monitor

# JMeter Perfmon Correlator v1.0


**Author:** Simon Cottrill

[https://github.com/tastyworm/jmeter_perfmon_correlator](https://github.com/tastyworm/jmeter_perfmon_correlator)

## Change History

| Version | Date       | Author          | Changes                                        |
|---------|------------|-----------------|------------------------------------------------|
| 1.0     | 2024-06-24 | Simon Cottrill  | Initial release                                |

## Description ##

This is a very simple utility built in Python with the Streamlit framework that correlates JMeter /JTL data with Windows Performance Monitor files in an attempt to help identify potential performance-issues.

### Features ###
- JMeter transaction filters
- Perfmon counter filters
- Visual chart creation for each correlation

### Pre-Requisites ###
- Python
- Poetry (installed using ```pip install poetry```)

### Installation ###
1. From the root folder of this repository type 'poetry update'

### How to start the application ###
1. Start the application by running ```streamlit run main.py```
1. A browser window should open, but if it doesn't go to the URL provided after starting rpum.
