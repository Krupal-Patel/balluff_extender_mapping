import streamlit as st

# Set page config as the first Streamlit command (for standalone mode)
st.set_page_config(layout="wide")

def handle_checkbox_change(port_num):
    """Callback to enforce single selection: uncheck all others when one is checked."""
    if st.session_state[f"check_{port_num}"]:  # If this one was checked
        for i in range(8):
            if i != port_num:
                st.session_state[f"check_{i}"] = False
    else:
        # If trying to uncheck the only selected one, re-check it (enforce at least one selected)
        st.session_state[f"check_{port_num}"] = True

def run_app():
    try:
        # Initialize session state at the top (before columns)
        if 'port_mode' not in st.session_state:
            st.session_state.port_mode = "8 Port"
        if 'initialized_checkboxes' not in st.session_state:
            for i in range(8):
                st.session_state[f"check_{i}"] = False
            # Set default selection on first run
            default_port = 2 if st.session_state.port_mode == "4 Port" else 0
            st.session_state[f"check_{default_port}"] = True
            st.session_state.initialized_checkboxes = True
            st.session_state.previous_mode = st.session_state.port_mode
        if 'io_configs' not in st.session_state:
            st.session_state.io_configs = {
                f"port_{i}": {"pin2": "Input", "pin4": "Input"} for i in range(8)
            }

        # Custom CSS for title visibility, left justification, and port label styling
        st.markdown(
            """
            <style>
            /* Title styling - increased top padding to avoid hiding */
            h1 { font-size: 24px !important; word-wrap: break-word; padding-top: 50px; padding-bottom: 10px; }
            /* Left justification for all column content */
            [data-testid="column"] div, [data-testid="column"] p, [data-testid="column"] span, .stText, .stRadio > label { text-align: left !important; }
            /* Compact layout */
            .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
            [data-testid="column"] { margin: 0px; padding: 0px; }
            .stText { margin-bottom: 0px; }
            .stRadio > div { margin: 0px; padding: 0px; flex-direction: column; align-items: flex-start; }
            /* Port label styling (different color and size) */
            .port-label { font-weight: bold; font-size: 16px; color: #007BFF; text-align: left; }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.title("App 1: IO Link Extender Configurator")

        # Main two-column layout (Col1 narrow, Col2 wider for combined config+tags)
        col1, col2 = st.columns([1, 2])

        # Column 1: Main Balluff (execute FIRST to set mode and selection before pre-compute)
        with col1:
            st.subheader("Main Balluff")

            # Port mode selection
            st.session_state.port_mode = st.radio(
                "Select Port Mode:",
                ["4 Port", "8 Port"],
                index=1 if st.session_state.port_mode == "8 Port" else 0,
                horizontal=True
            )

            # Reset on mode change and select a default
            if st.session_state.get('previous_mode') != st.session_state.port_mode:
                for i in range(8):
                    st.session_state[f"check_{i}"] = False
                # Select first available as default
                default_port = 2 if st.session_state.port_mode == "4 Port" else 0
                st.session_state[f"check_{default_port}"] = True
                st.session_state.previous_mode = st.session_state.port_mode

            # Determine disabled ports
            is_4_port = st.session_state.port_mode == "4 Port"
            disabled_ports = [0, 1, 4, 5] if is_4_port else []

            # Sub-columns for port groups
            sub_col1, sub_col2 = st.columns(2)

            # Left sub-column: Ports 0-3 (no header)
            with sub_col1:
                for i in range(4):
                    st.checkbox(
                        f"Port {i}",
                        value=st.session_state[f"check_{i}"],
                        key=f"check_{i}",
                        disabled=(i in disabled_ports),
                        on_change=handle_checkbox_change,
                        args=(i,)
                    )

            # Right sub-column: Ports 4-7 (no header)
            with sub_col2:
                for i in range(4, 8):
                    st.checkbox(
                        f"Port {i}",
                        value=st.session_state[f"check_{i}"],
                        key=f"check_{i}",
                        disabled=(i in disabled_ports),
                        on_change=handle_checkbox_change,
                        args=(i,)
                    )

            # Display current selection (will be set below in pre-compute)
            # Placeholder; actual display after pre-compute

        # Pre-compute mappings and selected port (execute after Col1, for updated state)
        mapping_4port = {
            "Port 2": {"input": 8, "output": 6},
            "Port 3": {"input": 56, "output": 38},
            "Port 6": {"input": 104, "output": 70},
            "Port 7": {"input": 152, "output": 102}
        }
        mapping_8port = {
            "Port 0": {"input": 8, "output": 6},
            "Port 1": {"input": 56, "output": 38},
            "Port 2": {"input": 104, "output": 70},
            "Port 3": {"input": 152, "output": 102},
            "Port 4": {"input": 200, "output": 134},
            "Port 5": {"input": 248, "output": 166},
            "Port 6": {"input": 296, "output": 198},
            "Port 7": {"input": 344, "output": 230}
        }
        mapping = mapping_4port if is_4_port else mapping_8port

        selected_port = None
        for i in range(8):
            if st.session_state.get(f"check_{i}", False):
                selected_port = f"Port {i}"
                break

        base_input = mapping.get(selected_port, {}).get("input")
        base_output = mapping.get(selected_port, {}).get("output")

        # Custom bit mapping: (extender_port, pin) -> (main_byte, assigned_bit)
        bit_map = {
            (0, "pin2"): (0, 1), (0, "pin4"): (0, 0),
            (1, "pin2"): (0, 3), (1, "pin4"): (0, 2),
            (2, "pin2"): (0, 5), (2, "pin4"): (0, 4),
            (3, "pin2"): (0, 7), (3, "pin4"): (0, 6),
            (4, "pin2"): (1, 1), (4, "pin4"): (1, 0),
            (5, "pin2"): (1, 3), (5, "pin4"): (1, 2),
            (6, "pin2"): (1, 5), (6, "pin4"): (1, 4),
            (7, "pin2"): (1, 7), (7, "pin4"): (1, 6),
        }

        # Combined Column 2: Configurator + Tags (execute after pre-compute)
        with col2:
            st.subheader("Extender Balluff")

            # Grid layout for extender (configs + tags), with flat columns to avoid nesting issues
            for row in range(4):
                port_left = row * 2
                port_right = port_left + 1

                # Row for port labels (matching pin column widths for alignment, left-justified)
                label_cols = st.columns([1.3, 1.3, 0.3, 1.3, 1.3])
                with label_cols[0]:
                    st.markdown('<div class="port-label">Port {}</div>'.format(port_left), unsafe_allow_html=True)
                with label_cols[3]:
                    st.markdown('<div class="port-label">Port {}</div>'.format(port_right), unsafe_allow_html=True)

                # Row for pin labels, radios, and tags (left-justified)
                pin_cols = st.columns([1.3, 1.3, 0.3, 1.3, 1.3])

                # Left Port Pins
                pins_left = [("pin4", 0, port_left), ("pin2", 1, port_left)]
                for pin, col_idx, port_num in pins_left:
                    port_key = f"port_{port_num}"
                    with pin_cols[col_idx]:
                        st.text(pin.capitalize())
                        pin_state = st.radio(
                            f"{pin}_radio_{port_key}",
                            ["IN", "OUT"],
                            index=0 if st.session_state.io_configs[port_key][pin] == "Input" else 1,
                            label_visibility="collapsed"
                        )
                        st.session_state.io_configs[port_key][pin] = "Input" if pin_state == "IN" else "Output"
                        config = st.session_state.io_configs[port_key][pin]
                        if base_input is not None and base_output is not None:
                            main_byte, assigned_bit = bit_map[(port_num, pin)]
                            tag_bit = assigned_bit
                            array = "I" if config == "Input" else "O"
                            xxx = (base_input + main_byte) if config == "Input" else (base_output + main_byte)
                            tag = f"{array}.Data[{xxx}].{tag_bit}"
                        else:
                            tag = "N/A"
                        st.text(f"Tag: {tag}")

                # Empty center
                with pin_cols[2]:
                    pass

                # Right Port Pins
                pins_right = [("pin4", 3, port_right), ("pin2", 4, port_right)]
                for pin, col_idx, port_num in pins_right:
                    port_key = f"port_{port_num}"
                    with pin_cols[col_idx]:
                        st.text(pin.capitalize())
                        pin_state = st.radio(
                            f"{pin}_radio_{port_key}",
                            ["IN", "OUT"],
                            index=0 if st.session_state.io_configs[port_key][pin] == "Input" else 1,
                            label_visibility="collapsed"
                        )
                        st.session_state.io_configs[port_key][pin] = "Input" if pin_state == "IN" else "Output"
                        config = st.session_state.io_configs[port_key][pin]
                        if base_input is not None and base_output is not None:
                            main_byte, assigned_bit = bit_map[(port_num, pin)]
                            tag_bit = assigned_bit
                            array = "I" if config == "Input" else "O"
                            xxx = (base_input + main_byte) if config == "Input" else (base_output + main_byte)
                            tag = f"{array}.Data[{xxx}].{tag_bit}"
                        else:
                            tag = "N/A"
                        st.text(f"Tag: {tag}")

            # Compute the 2 bytes for extender (after all radios, so uses updated state)
            byte0 = 0  # For Pin 4 (bits 0-7: Ports 0-7, 1=Output, 0=Input)
            byte1 = 0  # For Pin 2 (bits 0-7: Ports 0-7, 1=Output, 0=Input)
            for i in range(8):
                port_key = f"port_{i}"
                if st.session_state.io_configs[port_key]["pin4"] == "Output":
                    byte0 |= (1 << i)
                if st.session_state.io_configs[port_key]["pin2"] == "Output":
                    byte1 |= (1 << i)

            # Display bytes at the bottom of Column 2
            st.markdown("### Configuration Bytes")
            st.write(f"Byte 0 (Pin 4 configs, Ports 0-7): {format(byte0, '08b')} (binary)")
            st.write(f"Byte 1 (Pin 2 configs, Ports 0-7): {format(byte1, '08b')} (binary)")

            # Reset button for extender
            if st.button("Reset All", use_container_width=True):
                st.session_state.io_configs = {
                    f"port_{i}": {"pin2": "Input", "pin4": "Input"} for i in range(8)
                }
                # Ensure a port is selected after reset
                if not any(st.session_state.get(f"check_{i}", False) for i in range(8)):
                    default_port = 2 if st.session_state.port_mode == "4 Port" else 0
                    st.session_state[f"check_{default_port}"] = True
                st.rerun()

            st.info("Changes are auto-saved in session state. Refresh to start over.")

        # Finish Column 1: Add display current selection and expander (after pre-compute)
        with col1:
            if selected_port:
                st.write(f"Currently selected: **{selected_port}**")
            else:
                st.write("No port selected.")

            # Optional Reference Tag Names (in expander)
            with st.expander("View Reference Tag Names"):
                st.write("Byte mapping for reference tag names based on port mode.")
                # Prepare data for mapping table
                mapping_data = [
                    {"Port": port, "Input Start": info["input"], "Output Start": info["output"]}
                    for port, info in mapping.items()
                ]
                st.table(mapping_data)
    
    except Exception as e:
        st.error(f"An error occurred in the app: {str(e)}. Please check your code or Streamlit version.")

# Run the app directly when this script is executed (for standalone mode)
if __name__ == "__main__":
    run_app()
