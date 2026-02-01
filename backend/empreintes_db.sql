-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : dim. 01 fév. 2026 à 20:59
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `empreintes_db`
--

-- --------------------------------------------------------

--
-- Structure de la table `empreinte`
--

CREATE TABLE `empreinte` (
  `id` int(11) NOT NULL,
  `utilisateur_id` int(11) NOT NULL,
  `image_path` varchar(255) NOT NULL,
  `date_upload` timestamp NOT NULL DEFAULT current_timestamp(),
  `doigt` varchar(20) DEFAULT NULL,
  `minutiae_data` text DEFAULT NULL,
  `match_percentage` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `empreinte`
--

INSERT INTO `empreinte` (`id`, `utilisateur_id`, `image_path`, `date_upload`, `doigt`, `minutiae_data`, `match_percentage`) VALUES
(1, 1, 'images/fvc/DB1_B/101_1.jpg', '2025-12-22 22:02:27', 'doigt1', NULL, NULL),
(2, 1, 'images/fvc/DB1_B/101_2.jpg', '2025-12-22 22:02:27', 'doigt2', NULL, NULL),
(3, 1, 'images/fvc/DB1_B/101_3.jpg', '2025-12-22 22:02:27', 'doigt3', NULL, NULL),
(4, 1, 'images/fvc/DB1_B/101_4.jpg', '2025-12-22 22:02:27', 'doigt4', NULL, NULL),
(5, 1, 'images/fvc/DB1_B/101_5.jpg', '2025-12-22 22:02:27', 'doigt5', NULL, NULL),
(6, 1, 'images/fvc/DB1_B/101_6.jpg', '2025-12-22 22:02:27', 'doigt6', NULL, NULL),
(7, 1, 'images/fvc/DB1_B/101_7.jpg', '2025-12-22 22:02:27', 'doigt7', NULL, NULL),
(8, 1, 'images/fvc/DB1_B/101_8.jpg', '2025-12-22 22:02:27', 'doigt8', NULL, NULL),
(9, 2, 'images/fvc/DB1_B/102_1.jpg', '2025-12-22 22:02:27', 'doigt1', NULL, NULL),
(10, 2, 'images/fvc/DB1_B/102_2.jpg', '2025-12-22 22:02:27', 'doigt2', NULL, NULL),
(11, 2, 'images/fvc/DB1_B/102_3.jpg', '2025-12-22 22:02:27', 'doigt3', NULL, NULL),
(12, 2, 'images/fvc/DB1_B/102_4.jpg', '2025-12-22 22:02:27', 'doigt4', NULL, NULL),
(13, 2, 'images/fvc/DB1_B/102_5.jpg', '2025-12-22 22:02:27', 'doigt5', NULL, NULL),
(14, 2, 'images/fvc/DB1_B/102_6.jpg', '2025-12-22 22:02:27', 'doigt6', NULL, NULL),
(15, 2, 'images/fvc/DB1_B/102_7.jpg', '2025-12-22 22:02:27', 'doigt7', NULL, NULL),
(16, 2, 'images/fvc/DB1_B/102_8.jpg', '2025-12-22 22:02:27', 'doigt8', NULL, NULL),
(17, 3, 'images/fvc/DB1_B/103_1.jpg', '2025-12-22 22:02:27', 'doigt1', NULL, NULL),
(18, 3, 'images/fvc/DB1_B/103_2.jpg', '2025-12-22 22:02:27', 'doigt2', NULL, NULL),
(19, 3, 'images/fvc/DB1_B/103_3.jpg', '2025-12-22 22:02:27', 'doigt3', NULL, NULL),
(20, 3, 'images/fvc/DB1_B/103_4.jpg', '2025-12-22 22:02:27', 'doigt4', NULL, NULL),
(21, 3, 'images/fvc/DB1_B/103_5.jpg', '2025-12-22 22:02:27', 'doigt5', NULL, NULL),
(22, 3, 'images/fvc/DB1_B/103_6.jpg', '2025-12-22 22:02:27', 'doigt6', NULL, NULL),
(23, 3, 'images/fvc/DB1_B/103_7.jpg', '2025-12-22 22:02:27', 'doigt7', NULL, NULL),
(24, 3, 'images/fvc/DB1_B/103_8.jpg', '2025-12-22 22:02:27', 'doigt8', NULL, NULL),
(25, 4, 'images/fvc/DB1_B/104_1.jpg', '2025-12-22 22:02:27', 'doigt1', NULL, NULL),
(26, 4, 'images/fvc/DB1_B/104_2.jpg', '2025-12-22 22:02:27', 'doigt2', NULL, NULL),
(27, 4, 'images/fvc/DB1_B/104_3.jpg', '2025-12-22 22:02:27', 'doigt3', NULL, NULL),
(28, 4, 'images/fvc/DB1_B/104_4.jpg', '2025-12-22 22:02:27', 'doigt4', NULL, NULL),
(29, 4, 'images/fvc/DB1_B/104_5.jpg', '2025-12-22 22:02:27', 'doigt5', NULL, NULL),
(30, 4, 'images/fvc/DB1_B/104_6.jpg', '2025-12-22 22:02:27', 'doigt6', NULL, NULL),
(31, 4, 'images/fvc/DB1_B/104_7.jpg', '2025-12-22 22:02:27', 'doigt7', NULL, NULL),
(32, 4, 'images/fvc/DB1_B/104_8.jpg', '2025-12-22 22:02:27', 'doigt8', NULL, NULL),
(33, 5, 'images/fvc/DB1_B/105_1.jpg', '2025-12-22 22:02:27', 'doigt1', NULL, NULL),
(34, 5, 'images/fvc/DB1_B/105_2.jpg', '2025-12-22 22:02:27', 'doigt2', NULL, NULL),
(35, 5, 'images/fvc/DB1_B/105_3.jpg', '2025-12-22 22:02:27', 'doigt3', NULL, NULL),
(36, 5, 'images/fvc/DB1_B/105_4.jpg', '2025-12-22 22:02:27', 'doigt4', NULL, NULL),
(37, 5, 'images/fvc/DB1_B/105_5.jpg', '2025-12-22 22:02:27', 'doigt5', NULL, NULL),
(38, 5, 'images/fvc/DB1_B/105_6.jpg', '2025-12-22 22:02:27', 'doigt6', NULL, NULL),
(39, 5, 'images/fvc/DB1_B/105_7.jpg', '2025-12-22 22:02:27', 'doigt7', NULL, NULL),
(40, 5, 'images/fvc/DB1_B/105_8.jpg', '2025-12-22 22:02:27', 'doigt8', NULL, NULL),
(41, 6, 'images/fvc/DB1_B/106_1.jpg', '2025-12-22 22:02:27', 'doigt1', NULL, NULL),
(42, 6, 'images/fvc/DB1_B/106_2.jpg', '2025-12-22 22:02:27', 'doigt2', NULL, NULL),
(43, 6, 'images/fvc/DB1_B/106_3.jpg', '2025-12-22 22:02:27', 'doigt3', NULL, NULL),
(44, 6, 'images/fvc/DB1_B/106_4.jpg', '2025-12-22 22:02:27', 'doigt4', NULL, NULL),
(45, 6, 'images/fvc/DB1_B/106_5.jpg', '2025-12-22 22:02:27', 'doigt5', NULL, NULL),
(46, 6, 'images/fvc/DB1_B/106_6.jpg', '2025-12-22 22:02:27', 'doigt6', NULL, NULL),
(47, 6, 'images/fvc/DB1_B/106_7.jpg', '2025-12-22 22:02:27', 'doigt7', NULL, NULL),
(48, 6, 'images/fvc/DB1_B/106_8.jpg', '2025-12-22 22:02:27', 'doigt8', NULL, NULL),
(49, 7, 'images/fvc/DB1_B/107_1.jpg', '2025-12-22 22:02:27', 'doigt1', NULL, NULL),
(50, 7, 'images/fvc/DB1_B/107_2.jpg', '2025-12-22 22:02:27', 'doigt2', NULL, NULL),
(51, 7, 'images/fvc/DB1_B/107_3.jpg', '2025-12-22 22:02:27', 'doigt3', NULL, NULL),
(52, 7, 'images/fvc/DB1_B/107_4.jpg', '2025-12-22 22:02:27', 'doigt4', NULL, NULL),
(53, 7, 'images/fvc/DB1_B/107_5.jpg', '2025-12-22 22:02:27', 'doigt5', NULL, NULL),
(54, 7, 'images/fvc/DB1_B/107_6.jpg', '2025-12-22 22:02:27', 'doigt6', NULL, NULL),
(55, 7, 'images/fvc/DB1_B/107_7.jpg', '2025-12-22 22:02:27', 'doigt7', NULL, NULL),
(56, 7, 'images/fvc/DB1_B/107_8.jpg', '2025-12-22 22:02:27', 'doigt8', NULL, NULL),
(57, 8, 'images/fvc/DB1_B/108_1.jpg', '2025-12-22 22:02:27', 'doigt1', NULL, NULL),
(58, 8, 'images/fvc/DB1_B/108_2.jpg', '2025-12-22 22:02:27', 'doigt2', NULL, NULL),
(59, 8, 'images/fvc/DB1_B/108_3.jpg', '2025-12-22 22:02:27', 'doigt3', NULL, NULL),
(60, 8, 'images/fvc/DB1_B/108_4.jpg', '2025-12-22 22:02:27', 'doigt4', NULL, NULL),
(61, 8, 'images/fvc/DB1_B/108_5.jpg', '2025-12-22 22:02:27', 'doigt5', NULL, NULL),
(62, 8, 'images/fvc/DB1_B/108_6.jpg', '2025-12-22 22:02:27', 'doigt6', NULL, NULL),
(63, 8, 'images/fvc/DB1_B/108_7.jpg', '2025-12-22 22:02:27', 'doigt7', NULL, NULL),
(64, 8, 'images/fvc/DB1_B/108_8.jpg', '2025-12-22 22:02:27', 'doigt8', NULL, NULL),
(65, 9, 'images/fvc/DB1_B/109_1.jpg', '2025-12-22 22:02:27', 'doigt1', NULL, NULL),
(66, 9, 'images/fvc/DB1_B/109_2.jpg', '2025-12-22 22:02:27', 'doigt2', NULL, NULL),
(67, 9, 'images/fvc/DB1_B/109_3.jpg', '2025-12-22 22:02:27', 'doigt3', NULL, NULL),
(68, 9, 'images/fvc/DB1_B/109_4.jpg', '2025-12-22 22:02:27', 'doigt4', NULL, NULL),
(69, 9, 'images/fvc/DB1_B/109_5.jpg', '2025-12-22 22:02:27', 'doigt5', NULL, NULL),
(70, 9, 'images/fvc/DB1_B/109_6.jpg', '2025-12-22 22:02:27', 'doigt6', NULL, NULL),
(71, 9, 'images/fvc/DB1_B/109_7.jpg', '2025-12-22 22:02:27', 'doigt7', NULL, NULL),
(72, 9, 'images/fvc/DB1_B/109_8.jpg', '2025-12-22 22:02:27', 'doigt8', NULL, NULL),
(73, 10, 'images/fvc/DB1_B/110_1.jpg', '2025-12-22 22:02:27', 'doigt1', NULL, NULL),
(74, 10, 'images/fvc/DB1_B/110_2.jpg', '2025-12-22 22:02:27', 'doigt2', NULL, NULL),
(75, 10, 'images/fvc/DB1_B/110_3.jpg', '2025-12-22 22:02:27', 'doigt3', NULL, NULL),
(76, 10, 'images/fvc/DB1_B/110_4.jpg', '2025-12-22 22:02:27', 'doigt4', NULL, NULL),
(77, 10, 'images/fvc/DB1_B/110_5.jpg', '2025-12-22 22:02:27', 'doigt5', NULL, NULL),
(78, 10, 'images/fvc/DB1_B/110_6.jpg', '2025-12-22 22:02:27', 'doigt6', NULL, NULL),
(79, 10, 'images/fvc/DB1_B/110_7.jpg', '2025-12-22 22:02:27', 'doigt7', NULL, NULL),
(80, 10, 'images/fvc/DB1_B/110_8.jpg', '2025-12-22 22:02:27', 'doigt8', NULL, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `utilisateur`
--

CREATE TABLE `utilisateur` (
  `id` int(11) NOT NULL,
  `nom` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `photo_profil` varchar(255) DEFAULT NULL,
  `date_creation` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `utilisateur`
--

INSERT INTO `utilisateur` (`id`, `nom`, `email`, `password`, `photo_profil`, `date_creation`) VALUES
(1, 'Adjo', 'adjo1@example.com', '', NULL, '2025-11-15 16:20:41'),
(2, 'Koffi', 'koffi2@example.com', '', NULL, '2025-11-15 16:20:41'),
(3, 'Aminata', 'aminata3@example.com', '', NULL, '2025-11-15 16:20:41'),
(4, 'Blaise', 'blaise4@example.com', '', NULL, '2025-11-15 16:20:41'),
(5, 'Fatou', 'fatou5@example.com', '', NULL, '2025-11-15 16:20:41'),
(6, 'Yao', 'yao6@example.com', '', NULL, '2025-11-15 16:20:41'),
(7, 'Djeneba', 'djeneba7@example.com', '', NULL, '2025-11-15 16:20:41'),
(8, 'Kodjo', 'kodjo8@example.com', '', NULL, '2025-11-15 16:20:41'),
(9, 'Salimata', 'salimata9@example.com', '', NULL, '2025-11-15 16:20:41'),
(10, 'Benoit', 'benoit10@example.com', '', NULL, '2025-11-15 16:20:41'),
(11, 'Aissatou', 'aissatou11@example.com', '', NULL, '2025-11-15 16:20:41'),
(12, 'Michel', 'michel12@example.com', '', NULL, '2025-11-15 16:20:41'),
(13, 'Nadia', 'nadia13@example.com', '', NULL, '2025-11-15 16:20:41'),
(14, 'Sena', 'sena14@example.com', '', NULL, '2025-11-15 16:20:41'),
(15, 'Alassane', 'alassane15@example.com', '', NULL, '2025-11-15 16:20:41'),
(16, 'Mariama', 'mariama16@example.com', '', NULL, '2025-11-15 16:20:41'),
(17, 'Pascal', 'pascal17@example.com', '', NULL, '2025-11-15 16:20:41'),
(18, 'Koumba', 'koumba18@example.com', '', NULL, '2025-11-15 16:20:41'),
(19, 'Jean', 'jean19@example.com', '', NULL, '2025-11-15 16:20:41'),
(20, 'Awa', 'awa20@example.com', '', NULL, '2025-11-15 16:20:41'),
(21, 'Olivier', 'olivier21@example.com', '', NULL, '2025-11-15 16:20:41'),
(22, 'Fanta', 'fanta22@example.com', '', NULL, '2025-11-15 16:20:41'),
(23, 'Tchala', 'tchala23@example.com', '', NULL, '2025-11-15 16:20:41'),
(24, 'Assiba', 'assiba24@example.com', '', NULL, '2025-11-15 16:20:41'),
(25, 'Luc', 'luc25@example.com', '', NULL, '2025-11-15 16:20:41'),
(26, 'Rokia', 'rokia26@example.com', '', NULL, '2025-11-15 16:20:41'),
(27, 'Emmanuel', 'emmanuel27@example.com', '', NULL, '2025-11-15 16:20:41'),
(28, 'Kadia', 'kadia28@example.com', '', NULL, '2025-11-15 16:20:41'),
(29, 'Gildas', 'gildas29@example.com', '', NULL, '2025-11-15 16:20:41'),
(30, 'Hawa', 'hawa30@example.com', '', NULL, '2025-11-15 16:20:41'),
(31, 'Oumar', 'oumar31@example.com', '', NULL, '2025-11-15 16:20:41'),
(32, 'Fatima', 'fatima32@example.com', '', NULL, '2025-11-15 16:20:41'),
(33, 'Alain', 'alain33@example.com', '', NULL, '2025-11-15 16:20:41'),
(34, 'Yasmine', 'yasmine34@example.com', '', NULL, '2025-11-15 16:20:41'),
(35, 'Franck', 'franck35@example.com', '', NULL, '2025-11-15 16:20:41'),
(36, 'Kadiatou', 'kadiatou36@example.com', '', NULL, '2025-11-15 16:20:41'),
(37, 'Patrick', 'patrick37@example.com', '', NULL, '2025-11-15 16:20:41'),
(38, 'Salma', 'salma38@example.com', '', NULL, '2025-11-15 16:20:41'),
(39, 'Jean-Marie', 'jeanmarie39@example.com', '', NULL, '2025-11-15 16:20:41'),
(40, 'Ruth', 'ruth40@example.com', '', NULL, '2025-11-15 16:20:41'),
(41, 'Blaise', 'blaise41@example.com', '', NULL, '2025-11-15 16:20:41'),
(42, 'Aminata', 'aminata42@example.com', '', NULL, '2025-11-15 16:20:41'),
(43, 'Kodjo', 'kodjo43@example.com', '', NULL, '2025-11-15 16:20:41'),
(44, 'Assita', 'assita44@example.com', '', NULL, '2025-11-15 16:20:41'),
(45, 'Michel', 'michel45@example.com', '', NULL, '2025-11-15 16:20:41'),
(46, 'Sita', 'sita46@example.com', '', NULL, '2025-11-15 16:20:41'),
(47, 'Yao', 'yao47@example.com', '', NULL, '2025-11-15 16:20:41'),
(48, 'Nadia', 'nadia48@example.com', '', NULL, '2025-11-15 16:20:41'),
(49, 'Alassane', 'alassane49@example.com', '', NULL, '2025-11-15 16:20:41'),
(50, 'Mariama', 'mariama50@example.com', '', NULL, '2025-11-15 16:20:41'),
(51, 'Pascal', 'pascal51@example.com', '', NULL, '2025-11-15 16:20:41'),
(52, 'Koumba', 'koumba52@example.com', '', NULL, '2025-11-15 16:20:41'),
(53, 'Jean', 'jean53@example.com', '', NULL, '2025-11-15 16:20:41'),
(54, 'Awa', 'awa54@example.com', '', NULL, '2025-11-15 16:20:41'),
(55, 'Olivier', 'olivier55@example.com', '', NULL, '2025-11-15 16:20:41'),
(56, 'Fanta', 'fanta56@example.com', '', NULL, '2025-11-15 16:20:41'),
(57, 'Tchala', 'tchala57@example.com', '', NULL, '2025-11-15 16:20:41'),
(58, 'Assiba', 'assiba58@example.com', '', NULL, '2025-11-15 16:20:41'),
(59, 'Luc', 'luc59@example.com', '', NULL, '2025-11-15 16:20:41'),
(60, 'Rokia', 'rokia60@example.com', '', NULL, '2025-11-15 16:20:41'),
(61, 'Emmanuel', 'emmanuel61@example.com', '', NULL, '2025-11-15 16:20:41'),
(62, 'Kadia', 'kadia62@example.com', '', NULL, '2025-11-15 16:20:41'),
(63, 'Gildas', 'gildas63@example.com', '', NULL, '2025-11-15 16:20:41'),
(64, 'Hawa', 'hawa64@example.com', '', NULL, '2025-11-15 16:20:41'),
(65, 'Oumar', 'oumar65@example.com', '', NULL, '2025-11-15 16:20:41'),
(66, 'Fatima', 'fatima66@example.com', '', NULL, '2025-11-15 16:20:41'),
(67, 'Alain', 'alain67@example.com', '', NULL, '2025-11-15 16:20:41'),
(68, 'Yasmine', 'yasmine68@example.com', '', NULL, '2025-11-15 16:20:41'),
(69, 'Franck', 'franck69@example.com', '', NULL, '2025-11-15 16:20:41'),
(70, 'Kadiatou', 'kadiatou70@example.com', '', NULL, '2025-11-15 16:20:41'),
(71, 'Patrick', 'patrick71@example.com', '', NULL, '2025-11-15 16:20:41'),
(72, 'Salma', 'salma72@example.com', '', NULL, '2025-11-15 16:20:41'),
(73, 'Jean-Marie', 'jeanmarie73@example.com', '', NULL, '2025-11-15 16:20:41'),
(74, 'Ruth', 'ruth74@example.com', '', NULL, '2025-11-15 16:20:41'),
(75, 'Blaise', 'blaise75@example.com', '', NULL, '2025-11-15 16:20:41'),
(76, 'Aminata', 'aminata76@example.com', '', NULL, '2025-11-15 16:20:41'),
(77, 'Kodjo', 'kodjo77@example.com', '', NULL, '2025-11-15 16:20:41'),
(78, 'Assita', 'assita78@example.com', '', NULL, '2025-11-15 16:20:41'),
(79, 'Michel', 'michel79@example.com', '', NULL, '2025-11-15 16:20:41'),
(80, 'Sita', 'sita80@example.com', '', NULL, '2025-11-15 16:20:41'),
(81, 'Yao', 'yao81@example.com', '', NULL, '2025-11-15 16:20:41'),
(82, 'Nadia', 'nadia82@example.com', '', NULL, '2025-11-15 16:20:41'),
(83, 'Alassane', 'alassane83@example.com', '', NULL, '2025-11-15 16:20:41'),
(84, 'Mariama', 'mariama84@example.com', '', NULL, '2025-11-15 16:20:41'),
(85, 'Pascal', 'pascal85@example.com', '', NULL, '2025-11-15 16:20:41'),
(86, 'Koumba', 'koumba86@example.com', '', NULL, '2025-11-15 16:20:41'),
(87, 'Jean', 'jean87@example.com', '', NULL, '2025-11-15 16:20:41'),
(88, 'Awa', 'awa88@example.com', '', NULL, '2025-11-15 16:20:41'),
(89, 'Olivier', 'olivier89@example.com', '', NULL, '2025-11-15 16:20:41'),
(90, 'Fanta', 'fanta90@example.com', '', NULL, '2025-11-15 16:20:41'),
(91, 'Tchala', 'tchala91@example.com', '', NULL, '2025-11-15 16:20:41'),
(92, 'Assiba', 'assiba92@example.com', '', NULL, '2025-11-15 16:20:41'),
(93, 'Luc', 'luc93@example.com', '', NULL, '2025-11-15 16:20:41'),
(94, 'Rokia', 'rokia94@example.com', '', NULL, '2025-11-15 16:20:41'),
(95, 'Emmanuel', 'emmanuel95@example.com', '', NULL, '2025-11-15 16:20:41'),
(96, 'Kadia', 'kadia96@example.com', '', NULL, '2025-11-15 16:20:41'),
(97, 'Gildas', 'gildas97@example.com', '', NULL, '2025-11-15 16:20:41'),
(98, 'Hawa', 'hawa98@example.com', '', NULL, '2025-11-15 16:20:41'),
(99, 'Oumar', 'oumar99@example.com', '', NULL, '2025-11-15 16:20:41'),
(100, 'Fatima', 'fatima100@example.com', '', NULL, '2025-11-15 16:20:41'),
(102, 'DJOTAN Anette', 'anettedjotan1@gmail.com', '$2b$12$cqaPHdS6cl3DQWx6mgyQXuMIWjOPx4pnDFYPjh1in4Vq..TqiJqBS', '/uploads/profiles/c5056f16-9f48-4ca5-9120-0d07c0b894b6.webp', '2025-11-21 20:26:54'),
(104, 'ALLOHA Paul', 'anettedjotan2@gmail.com', '$2b$12$GYKFu9UTPZbq7zy7GWW4xuu8dr2fvlkzoYP2ld569Hq20.vM8OKDu', '/uploads/profiles/8dbe8a19-f8cd-4136-932b-155fa72abde1.png', '2025-11-21 20:35:49'),
(105, 'TOSSA Fanck', 'djotananette27@gmail.com', '$2b$12$POzxvm800GwXtNHTjfxree.ZVEJ5Jy6xh9qRiGQk.IVToj6ydmirC', '/uploads/profiles/e14d7dd9-7680-4c9c-85d3-c46ae81ef58d.png', '2025-11-21 20:46:37'),
(106, 'TOSSI Jean', 'anniedjotan@gmail.com', '$2b$12$yV/TN83rjmJnfLx3VAM70OoAf0eTy7Y1.qRHZpHVdUdyTaD.EKi/G', '/uploads/profiles/3304e291-9124-4f5c-9c5f-134bde89a72b.png', '2025-11-24 07:28:10'),
(107, 'TOSSI Jean', 'aniedjotan@gmail.com', '$2b$12$Tbdg9iLAlIVcf7kjJAVN6OLLeVyyCRMyNx5d2wJHhJ5gKiSQBvNfW', '/uploads/profiles/345b5922-acc9-4532-a774-361388f77e82.png', '2025-11-24 07:29:38'),
(108, 'TTTT aaaa', 'anettedjotan71@gmail.com', '$2b$12$6./hyz7FNghSPwgZvl8lpe2VyK6l3uVJzrgJFyjBlDM/3YjIJ6M2W', '/uploads/profiles/71adcb5d-dfdb-490d-a8ae-12268bda7097.png', '2025-11-24 07:34:53');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `empreinte`
--
ALTER TABLE `empreinte`
  ADD PRIMARY KEY (`id`),
  ADD KEY `utilisateur_id` (`utilisateur_id`);

--
-- Index pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `empreinte`
--
ALTER TABLE `empreinte`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=81;

--
-- AUTO_INCREMENT pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=109;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `empreinte`
--
ALTER TABLE `empreinte`
  ADD CONSTRAINT `empreinte_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateur` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
