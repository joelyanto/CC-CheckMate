-- phpMyAdmin SQL Dump
-- version 4.8.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 24 Nov 2024 pada 15.53
-- Versi server: 10.1.32-MariaDB
-- Versi PHP: 5.6.36

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `schools`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `attendance`
--

CREATE TABLE `attendance` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `status` enum('Hadir','Tidak Hadir','Terlambat') NOT NULL,
  `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data untuk tabel `attendance`
--

INSERT INTO `attendance` (`id`, `student_id`, `status`, `date`) VALUES
(1, 2, 'Terlambat', '2024-11-24 21:53:15'),
(2, 1, 'Terlambat', '2024-11-24 21:51:12');

-- --------------------------------------------------------

--
-- Struktur dari tabel `guru`
--

CREATE TABLE `guru` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `qualification` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data untuk tabel `guru`
--

INSERT INTO `guru` (`id`, `user_id`, `subject`, `qualification`) VALUES
(1, 4, NULL, NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `orang_tua`
--

CREATE TABLE `orang_tua` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `student_id` int(11) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `address` text,
  `last_message` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data untuk tabel `orang_tua`
--

INSERT INTO `orang_tua` (`id`, `user_id`, `student_id`, `phone_number`, `address`, `last_message`) VALUES
(1, 7, 1, '081234567890', 'JL. Mawar', 'Siswa Raffi Terlambat pada 2024-11-24 21:51:12'),
(2, 8, 2, '081234567891', 'JL. Melati', 'Siswa Nagita Terlambat pada 2024-11-24 21:53:15');

-- --------------------------------------------------------

--
-- Struktur dari tabel `siswa`
--

CREATE TABLE `siswa` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `class` varchar(50) DEFAULT NULL,
  `grade` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data untuk tabel `siswa`
--

INSERT INTO `siswa` (`id`, `user_id`, `class`, `grade`) VALUES
(1, 1, NULL, NULL),
(2, 5, NULL, NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `token_blacklist`
--

CREATE TABLE `token_blacklist` (
  `id` int(11) NOT NULL,
  `jti` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data untuk tabel `token_blacklist`
--

INSERT INTO `token_blacklist` (`id`, `jti`, `created_at`) VALUES
(1, '6035c050-f9c3-4b87-962f-2c88bb5da727', '2024-11-24 06:28:30'),
(2, 'b344e4de-6084-43c8-af70-5735040db9e0', '2024-11-24 06:45:17'),
(3, '03b6f2d8-4c25-497e-811f-59551b2fb714', '2024-11-24 06:52:23'),
(4, 'da4e3a9b-0d67-4766-b223-d93595ec12f8', '2024-11-24 06:53:27'),
(5, '5cd65a1f-6434-4ed0-9612-026c6b8a9e4c', '2024-11-24 08:05:33'),
(6, '231a9d2d-4a82-43d9-8ff0-6f277fbd9cf0', '2024-11-24 08:13:19'),
(7, '77a9b6c4-b7de-4412-aacd-ac8977f26898', '2024-11-24 13:52:41'),
(8, '899177f7-d682-47e4-9c85-c708839889a9', '2024-11-24 14:49:32');

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('siswa','guru','orang_tua') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `role`) VALUES
(1, 'raffi', 'raffi@example.com', 'scrypt:32768:8:1$s3A353PNZWIV6Xxq$a55c0d3a905101236595428b9c9d709f1b0f751a61239535b8c3a4c5676e69b8ad81701f05ade1dbd983ece3eeef6c1711ad1a2d0c3d26164cc38efe1b1fcb5a', 'siswa'),
(4, 'joel', 'joel@example.com', 'scrypt:32768:8:1$zy75GgcrRXhDOxyM$f56f57a2dda242486a9dd3a3edf648fd20ef004ee604f889a0d92e12208dac8ff2c5e89d851aa8a3a95be1a28e48e1e9f3fdf916d35fdba1f9d35fa9e36f9fc3', 'guru'),
(5, 'nagita', 'nagita@example.com', 'scrypt:32768:8:1$VnpPlctqTRw4cBy5$87ec342f87b1bae720441d93083d79aef152d524a1cc7b5503fb0b2af1d37e3c2e13a6d9b6e0cc2b17a273caff92b789836ccd33980aba10637310e9ad5530c8', 'siswa'),
(7, 'bapak raffi', 'bapak_raffi@example.com', 'scrypt:32768:8:1$FMhDsrgnLi3EnSac$e03f0a2451d1e3ac6385154b8abdc3516265dde790ed5d09fec9d959fc41d50d0ce2d295f43dd4f958afc226df5e7827a0199ba75da4a732c34a988cd24bf0e7', 'orang_tua'),
(8, 'bapak nagita', 'bapak_nagita@example.com', 'scrypt:32768:8:1$06eYWUIcy294b3Qb$1db55578aa083ca21403905e28930e461e95236fb107d688e42ead6484ed0e380cf255e4af0349be08c1ae3d7a5a7f298a50e86a7ab5cc1c8876c00ecd0cab90', 'orang_tua');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`);

--
-- Indeks untuk tabel `guru`
--
ALTER TABLE `guru`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indeks untuk tabel `orang_tua`
--
ALTER TABLE `orang_tua`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `student_id` (`student_id`);

--
-- Indeks untuk tabel `siswa`
--
ALTER TABLE `siswa`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indeks untuk tabel `token_blacklist`
--
ALTER TABLE `token_blacklist`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `attendance`
--
ALTER TABLE `attendance`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `guru`
--
ALTER TABLE `guru`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `orang_tua`
--
ALTER TABLE `orang_tua`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `siswa`
--
ALTER TABLE `siswa`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `token_blacklist`
--
ALTER TABLE `token_blacklist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `attendance`
--
ALTER TABLE `attendance`
  ADD CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `siswa` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `guru`
--
ALTER TABLE `guru`
  ADD CONSTRAINT `guru_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `orang_tua`
--
ALTER TABLE `orang_tua`
  ADD CONSTRAINT `orang_tua_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `orang_tua_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `siswa` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `siswa`
--
ALTER TABLE `siswa`
  ADD CONSTRAINT `siswa_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
