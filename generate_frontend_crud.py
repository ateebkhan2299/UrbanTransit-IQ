import os

frontend_pages_dir = r"c:\Users\USER\Desktop\techwiz\frontend\src\pages"
os.makedirs(frontend_pages_dir, exist_ok=True)

templates = {
    "StopManagement.jsx": "Stops",
    "VehicleManagement.jsx": "Vehicles",
    "TripManagement.jsx": "Trips",
    "ScheduleManagement.jsx": "Schedules"
}

for filename, entity in templates.items():
    content = f"""import React, {{ useState, useEffect }} from 'react';
import axios from 'axios';
import {{ 
    Box, Typography, Button, Table, TableBody, TableCell, 
    TableHead, TableRow, Paper, Modal, TextField, Stack, IconButton 
}} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

const {filename.split('.')[0]} = () => {{
    const [items, setItems] = useState([]);
    const [openModal, setOpenModal] = useState(false);
    const [formData, setFormData] = useState({{}});
    
    useEffect(() => {{
        // Simulated fetch for {entity}
        setItems([
            {{ id: 1, name: 'Sample {entity} 1', status: 'Active' }},
            {{ id: 2, name: 'Sample {entity} 2', status: 'Inactive' }}
        ]);
    }}, []);

    return (
        <Box sx={{{{ p: 3 }}}}>
            <Box sx={{{{ display: 'flex', justifyContent: 'space-between', mb: 3 }}}}>
                <Typography variant="h4" fontWeight="bold">Manage {entity}</Typography>
                <Button variant="contained" startIcon={{<AddIcon />}} onClick={{() => setOpenModal(true)}}>
                    Add {entity}
                </Button>
            </Box>
            
            <Paper elevation={{3}}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell><b>ID</b></TableCell>
                            <TableCell><b>Name</b></TableCell>
                            <TableCell><b>Status</b></TableCell>
                            <TableCell><b>Actions</b></TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {{items.map(item => (
                            <TableRow key={{item.id}}>
                                <TableCell>{{item.id}}</TableCell>
                                <TableCell>{{item.name}}</TableCell>
                                <TableCell>{{item.status}}</TableCell>
                                <TableCell>
                                    <IconButton color="primary"><EditIcon /></IconButton>
                                    <IconButton color="error"><DeleteIcon /></IconButton>
                                </TableCell>
                            </TableRow>
                        ))}}
                    </TableBody>
                </Table>
            </Paper>

            <Modal open={{openModal}} onClose={{() => setOpenModal(false)}}>
                <Box sx={{{{ p: 4, bgcolor: 'background.paper', margin: '10% auto', width: 400, borderRadius: 2 }}}}>
                    <Typography variant="h6" mb={{2}}>Add/Edit {entity}</Typography>
                    <Stack spacing={{2}}>
                        <TextField label="Name" fullWidth />
                        <TextField label="Status" fullWidth />
                        <Button variant="contained" onClick={{() => setOpenModal(false)}}>Save</Button>
                    </Stack>
                </Box>
            </Modal>
        </Box>
    );
}};

export default {filename.split('.')[0]};
"""
    with open(os.path.join(frontend_pages_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

print("Frontend CRUD pages generated.")
