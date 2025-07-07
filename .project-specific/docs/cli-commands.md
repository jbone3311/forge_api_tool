# Forge API Tool - CLI Commands Reference

## Core Commands

### Status and Information
```bash
python cli.py status                    # Show system status and health
python cli.py test                      # Test API connection
```

### Configuration Management
```bash
python cli.py configs list              # List all configurations
python cli.py configs show <name>       # Show detailed configuration
python cli.py configs export <name> <file>  # Export configuration to file
python cli.py configs import <file>     # Import configuration from file
```

### Image Generation
```bash
python cli.py generate single <config> <prompt> [--seed]  # Generate single image
python cli.py generate batch <config> [--batch-size] [--batches]  # Generate batch
```

### Output Management
```bash
python cli.py outputs list              # List generated outputs
python cli.py analyze <image>           # Analyze image and extract parameters
```

### Wildcard Management
```bash
python cli.py wildcards list            # List available wildcard files
python cli.py wildcards preview <config> [--count]  # Preview wildcard resolution
```

## Web Dashboard Commands
```bash
python cli.py web start main            # Main dashboard
python cli.py web start bootstrap       # Bootstrap dashboard
python cli.py web start simplified      # Simplified dashboard
python cli.py web start comprehensive   # Comprehensive dashboard
python cli.py web start simple          # Simple dashboard
```

## Test Management
```bash
python cli.py tests run all             # Run all tests
python cli.py tests run comprehensive   # Run comprehensive tests
python cli.py tests run web             # Run web tests
```

## Queue Management
```bash
python cli.py queue status              # Show queue status
python cli.py queue clear               # Clear queue
```

## System Management
```bash
python cli.py system logs               # Show logs
python cli.py system cleanup            # Clean up system
```

## Utility Commands
```bash
python cli.py utils fix-encoding        # Fix weather.txt encoding
python cli.py utils quick-start         # Run quick start ritual
```

## Project-Specific Directories
- `wildcards/` - Wildcard files for dynamic prompt generation
- `web_dashboard/` - Web interface components
- `core/` - Core application modules
- `configs/` - Configuration templates
- `outputs/` - Generated images
- `logs/` - Application logs
- `tests/` - Test suite

## Project-Specific Scripts
- `cli.py` - Main CLI interface
- `tests/run_comprehensive_tests.py` - Comprehensive test runner
- `tests/run_all_tests.py` - All tests runner
- `scripts/fix_wildcard_encoding.py` - Wildcard encoding fix utility 