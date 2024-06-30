from tkinter import *
import customtkinter
import json
import yaml
import os
from tkinter import messagebox
from tkinter import filedialog

def toggle_move_to_error_visibility(min_file_size_entry, move_to_error_label, move_to_error_entry, event=None):
    if min_file_size_entry.get().strip():
        move_to_error_label.grid()
        move_to_error_entry.grid()
    else:
        move_to_error_label.grid_remove()
        move_to_error_entry.grid_remove()

# Set theme and color options
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.title('File Converter')
initial_width = 650
initial_height = 820
root.geometry(f'{initial_width}x{initial_height}')
root.resizable(False, False)  # Disable resizing (disables maximize button)

section_frames = []

# main Frame
content_frame = customtkinter.CTkFrame(root)
content_frame.pack(padx=10, pady=10, fill='both', expand=True)

# Create a frame to hold the horizontally aligned widgets at the top
horizontal_frame = customtkinter.CTkFrame(content_frame, fg_color="#2B2B2B")
horizontal_frame.pack(pady=40, fill='x', padx=10)

# Add widgets to the horizontal frame
my_label = customtkinter.CTkLabel(horizontal_frame, text="Workflows", font=("Helvetica", 18))
my_label.pack(side='left', padx=20)

save_btn = customtkinter.CTkButton(horizontal_frame, text="Save",command=lambda: save_workflows_to_yaml() ,width=70)
save_btn.pack(side='left', padx=20)

# Add New button
addnew_btn = customtkinter.CTkButton(horizontal_frame, text="Add New",command=lambda: create_form_section() ,width=70)
addnew_btn.pack(side='left', padx=20)

# Add edit button
edit_btn = customtkinter.CTkButton(horizontal_frame, text="Edit",command=lambda: edit_workflows() ,width=70)
edit_btn.pack(side='left', padx=20)

# Options for combobox
my_combo = customtkinter.CTkComboBox(horizontal_frame, values=["0"])
my_combo.pack(side='left', padx=20)

# Function to change the label text based on combobox value
def change_label(combobox, label):
    if combobox.get() == "async":
        label.configure(text="s3_path:")
    else:
        label.configure(text="workflow_id:")

# Function to toggle visibility of section frames
def toggle_section_visibility(event=None):
    selected_item = my_combo.get()
    if not selected_item:
        return
    selected_index = int(selected_item.split(':')[0])
    for i, frame in enumerate(section_frames):
        if i == selected_index:
            frame.pack(pady=10, padx=20, anchor='w', fill='x')
        else:
            frame.pack_forget()
            
def update_combo_values():
    names = []
    for i, frame in enumerate(section_frames):
        if len(frame.winfo_children()) > 1:
            fields_frame = frame.winfo_children()[1]
            if fields_frame.grid_size()[1] > 1:
                name_entry = fields_frame.grid_slaves(row=1, column=1)
                if name_entry:
                    name = name_entry[0].get()
                    names.append(f"{i}: {name}" if name else f"{i}")
    my_combo.configure(values=names if names else [""])

# Function to create a new form section
def create_form_section():
    # Create a frame for the entire section
    section_frame = customtkinter.CTkFrame(content_frame, fg_color="#2B2B2B", border_width=2)
    
    # Add the section frame to the end of the section_frames list
    section_frames.append(section_frame)
    
    # Toggle visibility to show only the new section
    toggle_section_visibility()
    
    # Add internal padding to the section frame (inside padding)
    section_frame.pack_configure(ipadx=10, ipady=20)

    # Create frame for workflow_type label and combobox
    cross_button_frame = customtkinter.CTkFrame(section_frame)
    cross_button_frame.pack(pady=10, padx=30, anchor='w', fill='x')

    cross_btn = customtkinter.CTkButton(cross_button_frame, text="X", width=40, fg_color="red", hover_color="maroon", command=lambda: remove_form(section_frame))
    cross_btn.pack(side='right', padx=30)

    # Create a frame for the label-entry pairs
    fields_frame = customtkinter.CTkFrame(section_frame)
    fields_frame.pack(padx=50, anchor='w', fill='x')

    file_parameter_location_frame = customtkinter.CTkFrame(section_frame)
    file_parameter_location_frame.pack(padx=50, anchor='w', fill='x')

    file_parameter_subitem_frame = customtkinter.CTkFrame(section_frame)
    file_parameter_subitem_frame.pack(padx=70, anchor='w', fill='x')

    location_label_frame = customtkinter.CTkFrame(section_frame)
    location_label_frame.pack(padx=50, anchor='w', fill='x')

    location_subitem_frame = customtkinter.CTkFrame(section_frame)
    location_subitem_frame.pack(padx=70, anchor='w', fill='x')

    # Define the label-entry pairs including nested structure
    fields = [
        ("workflow_type:", ["sync", "async"]),
        ("name:", None),
        ("cron:", None),
        ("workflow_id:", None)
    ]

    file_parameter_label = customtkinter.CTkLabel(file_parameter_location_frame, text="file_parameters:", font=("Helvetica", 18))
    file_parameter_label.pack(side='left')

    file_parameter_subitem_entrypair = [
        ("input_file_type:", None),
        ("output_file_type", None),
        ("target_filename:", None),
        ("minimum_file_size_in_bytes:", None),
        ("move_to_error_for_invalid_file:", ["True","False"])
    ]

    location_label = customtkinter.CTkLabel(location_label_frame, text="location:", font=("Helvetica", 18))
    location_label.pack(side='left')

    location_subitem_entrypair = [
        ("queue:", None),
        ("output:", None),
        ("archive:", None),
        ("error:", None)
    ]

    # Add label-entry pairs to the frame using grid layout for fields
    fields_row_index = 0
    workflow_type_combobox = None
    workflow_id_label = None
    for i, (label_text, content) in enumerate(fields):
        label = customtkinter.CTkLabel(fields_frame, text=label_text, font=("Helvetica", 18))
        label.grid(row=fields_row_index, column=0, pady=5, sticky='w')

        if content is None:
            entry = customtkinter.CTkEntry(fields_frame)
        else:
            entry = customtkinter.CTkComboBox(fields_frame, values=content)
            if label_text == "workflow_type:":
                workflow_type_combobox = entry

        entry.grid(row=fields_row_index, column=1, padx=10, pady=5, sticky='ew')

        if label_text == "workflow_id:":
            workflow_id_label = label

        fields_row_index += 1

    # Add label-entry pairs to file_parameter_subitems_frame 
    file_parameter_subitem_row_index = 0
    move_to_error_label = None
    move_to_error_entry = None
    for i, (label_text, content) in enumerate(file_parameter_subitem_entrypair):
        label = customtkinter.CTkLabel(file_parameter_subitem_frame, text=label_text, font=("Helvetica", 18))
        label.grid(row=file_parameter_subitem_row_index, column=0, pady=5, sticky='w')

        if content is None:
            entry = customtkinter.CTkEntry(file_parameter_subitem_frame)
        else:
            entry = customtkinter.CTkComboBox(file_parameter_subitem_frame, values=content)
            entry.set("False")
        entry.grid(row=file_parameter_subitem_row_index, column=1, padx=10, pady=5, sticky='ew')
        
        if label_text == "move_to_error_for_invalid_file:":
            move_to_error_label = label
            move_to_error_entry = entry
            # Initially hide the move_to_error field
            label.grid_remove()
            entry.grid_remove()
        elif label_text == "minimum_file_size_in_bytes:":
            min_file_size_entry = entry
        
        file_parameter_subitem_row_index += 1

    # Bind the function to the minimum_file_size_in_bytes entry
    min_file_size_entry.bind("<KeyRelease>", lambda event: toggle_move_to_error_visibility(min_file_size_entry, move_to_error_label, move_to_error_entry, event))
    # Add label-entry pairs to location_subitems_frame 
    location_subitem_row_index = 0
    for i, (label_text, content) in enumerate(location_subitem_entrypair):
        label = customtkinter.CTkLabel(location_subitem_frame, text=label_text, font=("Helvetica", 18))
        label.grid(row=location_subitem_row_index, column=0, pady=5, sticky='w')

        if content is None:
            entry = customtkinter.CTkEntry(location_subitem_frame)

        entry.grid(row=location_subitem_row_index, column=1, padx=10, pady=5, sticky='ew')
        location_subitem_row_index += 1

    # Ensure the columns expand to fill the available space
    fields_frame.grid_columnconfigure(1, weight=1)
    file_parameter_subitem_frame.grid_columnconfigure(1, weight=1)
    location_subitem_frame.grid_columnconfigure(1, weight=1)

    # Set initial border colors for required fields
    fields_frame.grid_slaves(row=1, column=1)[0].configure(placeholder_text="*required")  # name
    fields_frame.grid_slaves(row=2, column=1)[0].configure(placeholder_text="*required")  # cron
    fields_frame.grid_slaves(row=3, column=1)[0].configure(placeholder_text="*required")  # workflow_id / s3_path
    file_parameter_subitem_frame.grid_slaves(row=0, column=1)[0].configure(placeholder_text="*required")  # input_file_type
    location_subitem_frame.grid_slaves(row=0, column=1)[0].configure(placeholder_text="*required")  # queue
    location_subitem_frame.grid_slaves(row=2, column=1)[0].configure(placeholder_text="*required")  # archive
    location_subitem_frame.grid_slaves(row=3, column=1)[0].configure(placeholder_text="*required")  # error

    # Bind the name entry to update combo values when it changes
    name_entry = fields_frame.grid_slaves(row=1, column=1)[0]
    name_entry.bind("<KeyRelease>", lambda e: update_combo_values())

    # Update combobox values after creating all fields
    update_combo_values()
    
    combo_values = my_combo.cget("values")
    my_combo.set(combo_values[-1] if combo_values else "")

    # Make sure the new section is visible
    toggle_section_visibility()
     
    return (lambda event: toggle_move_to_error_visibility(min_file_size_entry, move_to_error_label, move_to_error_entry, event)), min_file_size_entry, move_to_error_label, move_to_error_entry

def remove_form(section_frame):
    if len(section_frames) > 1:
        index = section_frames.index(section_frame)
        section_frames.remove(section_frame)
        section_frame.destroy()
        
        # Update combobox values
        update_combo_values()
        
        # Set to the first available item or empty string
        combo_values = my_combo.cget("values")
        my_combo.set(combo_values[0] if combo_values else "")
        
        # Toggle visibility to show the new current section
        toggle_section_visibility()

# Bind the toggle_section_visibility function to the combobox
my_combo.configure(command=toggle_section_visibility)
def validate_workflows():
    all_valid = True
    error_messages = []
    names = set()

    for i, section in enumerate(section_frames):
        fields_frame = section.winfo_children()[1]
        file_parameter_subitem_frame = section.winfo_children()[3]
        location_subitem_frame = section.winfo_children()[5]

        # Validate required fields
        required_fields = {
            "name": fields_frame.grid_slaves(row=1, column=1)[0],
            "cron": fields_frame.grid_slaves(row=2, column=1)[0],
            "workflow_id/s3_path": fields_frame.grid_slaves(row=3, column=1)[0],
            "input_file_type": file_parameter_subitem_frame.grid_slaves(row=0, column=1)[0],
            "queue": location_subitem_frame.grid_slaves(row=0, column=1)[0],
            "archive": location_subitem_frame.grid_slaves(row=2, column=1)[0],
            "error": location_subitem_frame.grid_slaves(row=3, column=1)[0]
        }

        for field_name, widget in required_fields.items():
            value = widget.get().strip()
            if not value:
                widget.configure(border_color="red")
                all_valid = False
                error_messages.append(f"Workflow {i+1}: {field_name} is required")
            else:
                widget.configure(border_color="")

            # Check for unique name and no spaces
            if field_name == "name":
                if value in names:
                    widget.configure(border_color="red")
                    all_valid = False
                    error_messages.append(f"Workflow {i+1}: Name '{value}' is not unique")
                elif " " in value:
                    widget.configure(border_color="red")
                    all_valid = False
                    error_messages.append(f"Workflow {i+1}: Name cannot contain spaces")
                else:
                    names.add(value)

        # Validate min_file_size_in_bytes (must be a number)
        min_file_size_widget = file_parameter_subitem_frame.grid_slaves(row=3, column=1)[0]
        min_file_size = min_file_size_widget.get().strip()
        if min_file_size:
            try:
                int(min_file_size)
                min_file_size_widget.configure(border_color="")
            except ValueError:
                min_file_size_widget.configure(border_color="red")
                all_valid = False
                error_messages.append(f"Workflow {i+1}: minimum_file_size_in_bytes must be a number")

            # Only validate move_to_error_for_invalid_file if min_file_size is set
            move_to_error_widgets = file_parameter_subitem_frame.grid_slaves(row=4, column=1)
            if move_to_error_widgets:
                move_to_error_widget = move_to_error_widgets[0]
                move_to_error = move_to_error_widget.get().strip().lower()
                if move_to_error and move_to_error not in ['true', 'false']:
                    move_to_error_widget.configure(border_color="red")
                    all_valid = False
                    error_messages.append(f"Workflow {i+1}: move_to_error_for_invalid_file must be true or false")
                else:
                    move_to_error_widget.configure(border_color="")

    if not all_valid:
        messagebox.showerror("Validation Error", "\n".join(error_messages))

    return all_valid


def save_workflows_to_yaml():
    if validate_workflows():
        workflows = []
        for section in section_frames:
            workflow = {}
            
            # Collect basic fields 
            fields_frame = section.winfo_children()[1]
            for i in range(0, fields_frame.grid_size()[1]):
                label = fields_frame.grid_slaves(row=i, column=0)[0].cget("text").strip(":")
                entry = fields_frame.grid_slaves(row=i, column=1)[0]
                value = entry.get().strip()
                if value:  # Only add non-empty fields
                    workflow[label] = value
                    
            # Collect file parameters
            file_parameters = {}
            file_parameter_subitem_frame = section.winfo_children()[3]
            for i in range(0, file_parameter_subitem_frame.grid_size()[1]):
                label_widget = file_parameter_subitem_frame.grid_slaves(row=i, column=0)[0]
                entry_widget = file_parameter_subitem_frame.grid_slaves(row=i, column=1)[0]
                label = label_widget.cget("text").strip(":")
                value = entry_widget.get().strip()
                
                # Include all non-empty fields even if not visibility
                if value:
                    if label == "minimum_file_size_in_bytes":
                        file_parameters[label] = int(value)
                    elif label == "move_to_error_for_invalid_file":
                        file_parameters[label] = value.lower() == 'true'
                    else:
                        file_parameters[label] = value
                                    
            if file_parameters:  # Only add file_parameters if it's not empty
                workflow["file_parameters"] = file_parameters 

            # Collect location parameters 
            location = {}
            location_subitem_frame = section.winfo_children()[5]
            for i in range(0, location_subitem_frame.grid_size()[1]):
                label = location_subitem_frame.grid_slaves(row=i, column=0)[0].cget("text").strip(":")
                entry = location_subitem_frame.grid_slaves(row=i, column=1)[0]
                value = entry.get().strip()
                if value:  # Only add non-empty fields
                    location[label] = value
            
            if location:  # Only add location if not empty
                workflow["location"] = location

            workflows.append(workflow)
        
        
        
        # Create a single workflows_data dictionary with all workflows
        workflows_data = {"workflows": workflows}
        
        # Convert Python object to YAML
        yaml_data = yaml.dump(workflows_data, default_flow_style=False, sort_keys=False)
        
        # Remove quotes from the YAML output
        yaml_data = yaml.dump(yaml.safe_load(yaml_data), default_flow_style=False, sort_keys=False, default_style='')
        
        # Get the user's home directory
        home_dir = os.path.expanduser("~")
        
        # Create a default file name
        file_name = "workflows.yaml"
        
        # Full path for the file
        file_path = os.path.join(home_dir, "Downloads", file_name)
        
        # Ensure the file name is unique
        counter = 1
        while os.path.exists(file_path):
            file_name = f"workflows_{counter}.yaml"
            file_path = os.path.join(home_dir, "Downloads", file_name)
            counter += 1
        
        # Write YAML data to file
        with open(file_path, "w") as file:
            file.write(yaml_data)
        
        # print(f"YAML file saved as: {file_path}")
            


# def save_to_yaml(json_data):
#     # Convert JSON to Python object
#     data = json.loads(json_data)
    
#     # Convert Python object to YAML
#     yaml_data = yaml.dump(data, default_flow_style=False, sort_keys=False)
    
#     # Remove quotes from the YAML output
#     yaml_data = yaml.dump(yaml.safe_load(yaml_data), default_flow_style=False, sort_keys=False, default_style='')
    
#     # Get the user's home directory
#     home_dir = os.path.expanduser("~")
    
#     # Create a default file name
#     file_name = "workflows.yaml"
    
#     # Full path for the file
#     file_path = os.path.join(home_dir, "Downloads", file_name)
    
#     # Ensure the file name is unique
#     counter = 1
#     while os.path.exists(file_path):
#         file_name = f"workflows_{counter}.yaml"
#         file_path = os.path.join(home_dir, "Downloads", file_name)
#         counter += 1
    
#     # Write YAML data to file
#     with open(file_path, "w") as file:
#         file.write(yaml_data)
        
def edit_workflows():
    file_path = filedialog.askopenfilename(filetypes=[("YAML files", "*.yaml")])
    if file_path:
        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        
        if 'workflows' in yaml_data:
            populate_ui_with_workflows(yaml_data['workflows'])
        else:
            messagebox.showerror("Error", "Invalid YAML structure. 'workflows' not found.")

def populate_ui_with_workflows(workflows):
    # Clear existing sections
    for section in section_frames:
        section.destroy()
    section_frames.clear()
    
    for workflow in workflows:
        toggle_func, min_size_entry, error_label, error_entry = create_form_section()
        populate_section(section_frames[-1], workflow, toggle_func, min_size_entry, error_label, error_entry)

    
    # Update combo box
    update_combo_values()
    my_combo.set(my_combo.cget("values")[0])
    toggle_section_visibility()

def populate_section(section, workflow, toggle_func, min_size_entry, error_label, error_entry):
    fields_frame = section.winfo_children()[1]
    file_parameter_subitem_frame = section.winfo_children()[3]
    location_subitem_frame = section.winfo_children()[5]
    
    # Populate basic fields (unchanged)
    for i in range(fields_frame.grid_size()[1]):
        label = fields_frame.grid_slaves(row=i, column=0)[0].cget("text").strip(":")
        entry = fields_frame.grid_slaves(row=i, column=1)[0]
        if label in workflow:
            if isinstance(entry, customtkinter.CTkComboBox):
                entry.set(workflow[label])
            elif isinstance(entry, customtkinter.CTkEntry):
                entry.delete(0, END)
                entry.insert(0, workflow[label])
            entry.configure(border_color="")  # Reset border color
    
    # Populate file parameters
    if 'file_parameters' in workflow:
        min_file_size_entry = None
        move_to_error_label = None
        move_to_error_entry = None

        for i in range(file_parameter_subitem_frame.grid_size()[1]):
            label = file_parameter_subitem_frame.grid_slaves(row=i, column=0)[0]
            entry = file_parameter_subitem_frame.grid_slaves(row=i, column=1)[0]
            label_text = label.cget("text").strip(":")
            
            if label_text == "minimum_file_size_in_bytes":
                min_file_size_entry = entry
            elif label_text == "move_to_error_for_invalid_file":
                move_to_error_label = label
                move_to_error_entry = entry
            
            if label_text in workflow['file_parameters']:
                if isinstance(entry, customtkinter.CTkComboBox):
                    entry.set(str(workflow['file_parameters'][label_text]))
                elif isinstance(entry, customtkinter.CTkEntry):
                    entry.delete(0, END)
                    entry.insert(0, str(workflow['file_parameters'][label_text]))
                entry.configure(border_color="")

        # After populating all fields, set visibility
        # After populating all fields, set visibility
    if min_size_entry and error_label and error_entry:
        toggle_func(None)  # Initial call to set visibility
        
        if 'move_to_error_for_invalid_file' in workflow['file_parameters']:
            error_entry.set(str(workflow['file_parameters']['move_to_error_for_invalid_file']))
        else:
            error_entry.set("False")  # Default value if not specified

        # Bind the toggle function to the KeyRelease event
        min_size_entry.bind("<KeyRelease>", lambda event: toggle_func(event))

    # Populate location parameters 
    if 'location' in workflow:
        for i in range(location_subitem_frame.grid_size()[1]):
            label = location_subitem_frame.grid_slaves(row=i, column=0)[0].cget("text").strip(":")
            entry = location_subitem_frame.grid_slaves(row=i, column=1)[0]
            if label in workflow['location']:
                if isinstance(entry, customtkinter.CTkComboBox):
                    entry.set(workflow['location'][label])
                elif isinstance(entry, customtkinter.CTkEntry):
                    entry.delete(0, END)
                    entry.insert(0, workflow['location'][label])
                entry.configure(border_color="")          
    
create_form_section()
root.mainloop()