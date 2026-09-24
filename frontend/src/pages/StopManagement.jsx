import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
    Box, Typography, Button, Table, TableBody, TableCell, 
    TableHead, TableRow, Paper, Modal, TextField, Stack, IconButton 
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

const StopManagement = () => {
    const [items, setItems] = useState([]);
    const [openModal, setOpenModal] = useState(false);
    const [formData, setFormData] = useState({});
    
    useEffect(() => {
        // Simulated fetch for Stops
        setItems([
            { id: 1, name: 'Sample Stops 1', status: 'Active' },
            { id: 2, name: 'Sample Stops 2', status: 'Inactive' }
        ]);
    }, []);

    return (
        <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h4" fontWeight="bold">Manage Stops</Typography>
                <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenModal(true)}>
                    Add Stops
                </Button>
            </Box>
            
            <Paper elevation={3}>
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
                        {items.map(item => (
                            <TableRow key={item.id}>
                                <TableCell>{item.id}</TableCell>
                                <TableCell>{item.name}</TableCell>
                                <TableCell>{item.status}</TableCell>
                                <TableCell>
                                    <IconButton color="primary"><EditIcon /></IconButton>
                                    <IconButton color="error"><DeleteIcon /></IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </Paper>

            <Modal open={openModal} onClose={() => setOpenModal(false)}>
                <Box sx={{ p: 4, bgcolor: 'background.paper', margin: '10% auto', width: 400, borderRadius: 2 }}>
                    <Typography variant="h6" mb={2}>Add/Edit Stops</Typography>
                    <Stack spacing={2}>
                        <TextField label="Name" fullWidth />
                        <TextField label="Status" fullWidth />
                        <Button variant="contained" onClick={() => setOpenModal(false)}>Save</Button>
                    </Stack>
                </Box>
            </Modal>
        </Box>
    );
};

export default StopManagement;
