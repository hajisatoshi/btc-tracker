# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-XX

### Added
- **Multi-Currency Support**: Added EUR and GBP currency support
- **Currency Filtering**: Filter transactions by currency type
- **Enhanced Summary View**: Display portfolio summary in any supported currency
- **Improved Transaction Management**: Separate savings and spending tracking
- **Real-time EUR/GBP Pricing**: Live Bitcoin prices in Euro and British Pound
- **Advanced Currency Conversion**: Automatic conversion between all supported currencies
- **Production Build System**: PyInstaller-based executable generation
- **Comprehensive Testing**: Enhanced error handling and validation

### Changed
- **UI/UX Improvements**: Redesigned interface with tabbed navigation
- **Database Schema**: Enhanced to support multiple currencies
- **API Endpoints**: Updated to handle EUR/GBP data
- **Transaction Forms**: Support for multi-currency input
- **Portfolio Calculations**: Net position calculations across all currencies

### Fixed
- **Session Management**: Improved JWT token handling with 8-hour expiration
- **Error Handling**: Better error messages and user feedback
- **Authorization Issues**: Fixed missing authorization header errors
- **Data Validation**: Enhanced input validation for all forms

### Security
- **Authentication**: Improved JWT token security
- **Input Validation**: Enhanced validation for all user inputs
- **Password Security**: Strengthened password hashing

## [1.0.0] - 2024-XX-XX

### Added
- **Initial Release**: Basic Bitcoin portfolio tracking
- **Real-time Pricing**: Integration with CoinGecko API
- **Transaction Management**: Add, edit, delete Bitcoin transactions
- **Portfolio Summary**: Basic portfolio overview
- **Database Storage**: SQLite-based local storage
- **User Authentication**: Basic login/register functionality
- **Desktop Integration**: Launch from applications menu
- **CSV Import/Export**: Basic data import/export capabilities

### Features
- USD and CAD currency support
- Basic transaction history
- Profit/loss calculations
- Clean GUI interface
- Local data persistence

---

## Release Notes

### Version 2.0.0 - Production Release

This is the first production-ready release of BTC Portfolio Tracker, featuring:

- **Complete Multi-Currency Support**: Full EUR and GBP integration
- **Professional UI**: Polished interface with advanced features
- **Production Build**: Executable files for Windows, macOS, and Linux
- **Enhanced Security**: Improved authentication and data protection
- **Comprehensive Documentation**: Complete setup and usage guides

### Upgrade Guide

If upgrading from version 1.x:

1. **Database Migration**: The application will automatically migrate your existing data
2. **New Features**: Explore the new multi-currency features in the Summary tab
3. **Interface Changes**: Familiarize yourself with the new tabbed interface
4. **Currency Settings**: Set your preferred display currency in the Summary tab

### Known Issues

- Currency conversion rates are approximate and for display purposes
- Some legacy transaction data may need manual currency assignment
- First-time startup may take longer due to database migration

### Future Roadmap

- **v2.1.0**: Enhanced reporting and analytics
- **v2.2.0**: Data export improvements and backup features
- **v2.3.0**: Advanced charting and visualization
- **v3.0.0**: Cloud synchronization and mobile app support
