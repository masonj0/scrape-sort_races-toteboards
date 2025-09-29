import { Router, Request, Response } from 'express';

// ==============================================================================
// == API Routes for Race Data
// ==============================================================================
// This module defines all data-centric endpoints for the Checkmate application.
// ==============================================================================

const router = Router();

// --- MOCK DATA (for immediate functionality) ---
// In the future, this will be replaced with calls to a DatabaseService.
const MOCK_QUALIFIED_RACES = [
    { raceId: 'R1_AQU', trackName: 'Aqueduct', raceNumber: 1, postTime: '2025-09-29T18:00:00Z', checkmateScore: 85.2 },
    { raceId: 'R3_GP', trackName: 'Gulfstream Park', raceNumber: 3, postTime: '2025-09-29T18:30:00Z', checkmateScore: 79.5 },
];

const MOCK_ALL_RACES = [
    ...MOCK_QUALIFIED_RACES,
    { raceId: 'R2_AQU', trackName: 'Aqueduct', raceNumber: 2, postTime: '2025-09-29T18:15:00Z', checkmateScore: 60.0 },
];


/**
 * @route   GET /api/races/qualified
 * @desc    Get all races that meet the Checkmate qualification score
 * @access  Public
 */
router.get('/races/qualified', (req: Request, res: Response) => {
    try {
        // TODO: Replace with live data query
        res.status(200).json(MOCK_QUALIFIED_RACES);
    } catch (error) {
        console.error("Error fetching qualified races:", error);
        res.status(500).json({ message: "Error fetching qualified races" });
    }
});

/**
 * @route   GET /api/races/all
 * @desc    Get all races collected in the last cycle
 * @access  Public
 */
router.get('/races/all', (req: Request, res: Response) => {
    try {
        // TODO: Replace with live data query
        res.status(200).json(MOCK_ALL_RACES);
    } catch (error) {
        console.error("Error fetching all races:", error);
        res.status(500).json({ message: "Error fetching all races" });
    }
});

export default router;