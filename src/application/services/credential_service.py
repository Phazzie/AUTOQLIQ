            # Convert numeric args from string if needed (APScheduler might handle this)
            # Using stricter validation to ensure only valid numeric strings are converted
            import re  # Consider moving this import to the top of the file if not already done
            for k, v in trigger_args.items():
                if isinstance(v, str):
                    if re.fullmatch(r'-?\d+', v):
                        trigger_args[k] = int(v)
                    elif re.fullmatch(r'-?\d*\.\d+', v):
                        trigger_args[k] = float(v)

