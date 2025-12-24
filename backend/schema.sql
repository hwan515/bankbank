CREATE TABLE `products_financialcompany` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `dcls_month` varchar(6) NOT NULL,
  `fin_co_no` varchar(20) NOT NULL UNIQUE,
  `kor_co_nm` varchar(200) NOT NULL,
  `dcls_chrg_man` longtext NOT NULL,
  `homp_url` longtext NOT NULL,
  `cal_tel` varchar(100) NOT NULL
);

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL PRIMARY KEY,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
);

CREATE TABLE `accounts_user` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) NULL,
  `is_superuser` bool NOT NULL,
  `username` varchar(150) NOT NULL UNIQUE,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` bool NOT NULL,
  `is_active` bool NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `age` integer UNSIGNED NULL,
  `sex` varchar(1) NULL,
  `greeting` longtext NULL
);

CREATE TABLE `accounts_user_deposit_products` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `user_id` bigint NOT NULL,
  `depositproducts_id` bigint NOT NULL
);

CREATE TABLE `accounts_user_saving_products` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `user_id` bigint NOT NULL,
  `savingproducts_id` bigint NOT NULL
);

CREATE TABLE `accounts_user_user_permissions` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `user_id` bigint NOT NULL,
  `permission_id` integer NOT NULL
);

CREATE TABLE `accounts_information` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `user_id` bigint NOT NULL,
  `title` longtext NOT NULL,
  `content` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
);

CREATE TABLE `products_depositproducts` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `dcls_month` varchar(6) NOT NULL,
  `fin_prdt_cd` varchar(100) NOT NULL UNIQUE,
  `kor_co_nm` longtext NOT NULL,
  `fin_prdt_nm` longtext NOT NULL,
  `etc_note` longtext NOT NULL,
  `join_deny` integer NOT NULL,
  `join_member` longtext NOT NULL,
  `join_way` longtext NOT NULL,
  `spcl_cnd` longtext NOT NULL
);

CREATE TABLE `products_depositoptions` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `product_id` bigint NOT NULL,
  `fin_prdt_cd` varchar(100) NOT NULL,
  `intr_rate_type_nm` varchar(100) NOT NULL,
  `intr_rate` numeric(5, 2) NULL,
  `intr_rate2` numeric(5, 2) NULL,
  `save_trm` integer NOT NULL
);

CREATE TABLE `products_savingproducts` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `dcls_month` varchar(6) NOT NULL,
  `fin_prdt_cd` varchar(100) NOT NULL UNIQUE,
  `kor_co_nm` longtext NOT NULL,
  `fin_prdt_nm` longtext NOT NULL,
  `etc_note` longtext NOT NULL,
  `join_deny` integer NOT NULL,
  `join_member` longtext NOT NULL,
  `join_way` longtext NOT NULL,
  `spcl_cnd` longtext NOT NULL,
  `max_limit` bigint NULL
);

CREATE TABLE `products_savingoptions` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `product_id` bigint NOT NULL,
  `fin_prdt_cd` varchar(100) NOT NULL,
  `intr_rate_type_nm` varchar(100) NOT NULL,
  `rsrv_type_nm` varchar(100) NOT NULL,
  `intr_rate` numeric(5, 2) NULL,
  `intr_rate2` numeric(5, 2) NULL,
  `save_trm` integer NOT NULL
);

CREATE TABLE `products_depositsubscription` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `user_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  `term_months` integer NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
);

CREATE TABLE `products_savingsubscription` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `user_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  `term_months` integer NULL,
  `rsrv_type` varchar(20) NOT NULL,
  `monthly_amount` integer NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
);

CREATE TABLE `cards_card` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `gorilla_id` integer NOT NULL UNIQUE,
  `name` varchar(200) NOT NULL,
  `company` varchar(100) NOT NULL,
  `card_type` varchar(20) NOT NULL,
  `annual_fee` varchar(200) NOT NULL,
  `annual_fee_min` integer NOT NULL,
  `min_spending` integer NOT NULL,
  `benefits_summary` longtext NOT NULL,
  `benefits_json` json NOT NULL,
  `structured_benefit` json NOT NULL,
  `categories` json NOT NULL,
  `ranking` integer NULL,
  `crawled_at` datetime(6) NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
);

CREATE TABLE `cards_userprofile` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `user_id` bigint NOT NULL UNIQUE,
  `monthly_spend` integer NOT NULL,
  `category_weights` json NOT NULL,
  `fee_tolerance` integer NOT NULL,
  `min_spend_tolerance` integer NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
);

CREATE TABLE `cards_userevent` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `user_id` bigint NULL,
  `card_id` bigint NOT NULL,
  `event_type` varchar(10) NOT NULL,
  `context` json NOT NULL,
  `session_id` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL
);

CREATE TABLE `cards_recommendationlog` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `user_id` bigint NULL,
  `session_id` varchar(100) NOT NULL,
  `query_text` longtext NOT NULL,
  `filters` json NOT NULL,
  `result_card_ids` json NOT NULL,
  `result_scores` json NOT NULL,
  `processing_time_ms` integer NOT NULL,
  `created_at` datetime(6) NOT NULL
);

CREATE TABLE `cards_cardembeddingstate` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `card_id` bigint NOT NULL UNIQUE,
  `doc_id` varchar(100) NOT NULL UNIQUE,
  `embedding_version` integer NOT NULL,
  `content_hash` varchar(64) NOT NULL,
  `needs_embedding` bool NOT NULL,
  `last_indexed_at` datetime(6) NULL,
  `updated_at` datetime(6) NOT NULL
);

CREATE TABLE `community_post` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `author_id` bigint NOT NULL,
  `board_type` varchar(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `content` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
);

CREATE TABLE `community_post_like_users` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `post_id` bigint NOT NULL,
  `user_id` bigint NOT NULL
);

CREATE TABLE `community_post_dislike_users` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `post_id` bigint NOT NULL,
  `user_id` bigint NOT NULL
);

CREATE TABLE `community_comment` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `post_id` bigint NOT NULL,
  `author_id` bigint NOT NULL,
  `content` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
);

CREATE TABLE `community_comment_like_users` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `comment_id` bigint NOT NULL,
  `user_id` bigint NOT NULL
);

CREATE TABLE `community_comment_dislike_users` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `comment_id` bigint NOT NULL,
  `user_id` bigint NOT NULL
);

CREATE TABLE `chats_chatroom` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `name` varchar(100) NOT NULL,
  `is_lobby` bool NOT NULL,
  `is_dm` bool NOT NULL,
  `dm_key` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `is_public` bool NOT NULL,
  `last_message_at` datetime(6) NULL
);

CREATE TABLE `chats_chatroom_members` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `chatroom_id` bigint NOT NULL,
  `user_id` bigint NOT NULL
);

CREATE TABLE `chats_chatmessage` (
  `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `room_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `content` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL
);

CREATE TABLE `authtoken_token` (
  `key` varchar(40) NOT NULL PRIMARY KEY,
  `user_id` bigint NOT NULL UNIQUE,
  `created` datetime(6) NOT NULL
);

CREATE TABLE `account_emailaddress` (
  `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `user_id` bigint NOT NULL,
  `email` varchar(254) NOT NULL,
  `verified` bool NOT NULL,
  `primary` bool NOT NULL
);

CREATE TABLE `account_emailconfirmation` (
  `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `email_address_id` integer NOT NULL,
  `created` datetime(6) NOT NULL,
  `sent` datetime(6) NULL,
  `key` varchar(64) NOT NULL UNIQUE
);

CREATE TABLE `socialaccount_socialapp` (
  `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `provider` varchar(30) NOT NULL,
  `provider_id` varchar(200) NOT NULL,
  `name` varchar(40) NOT NULL,
  `client_id` varchar(191) NOT NULL,
  `secret` varchar(191) NOT NULL,
  `key` varchar(191) NOT NULL,
  `settings` json NOT NULL
);

CREATE TABLE `socialaccount_socialaccount` (
  `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `user_id` bigint N_
