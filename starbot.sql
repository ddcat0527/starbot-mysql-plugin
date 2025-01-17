SET NAMES utf8mb4;
SET
FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for bot
-- ----------------------------
DROP TABLE IF EXISTS `bot`;
CREATE TABLE `bot`
(
    `id`  bigint(0) NOT NULL AUTO_INCREMENT,
    `bot` bigint(0) NULL DEFAULT NULL,
    `uid` bigint(0) NULL DEFAULT NULL,
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 53 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for dynamic_update
-- ----------------------------
DROP TABLE IF EXISTS `dynamic_update`;
CREATE TABLE `dynamic_update`
(
    `id`      varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `uid`     bigint(0) NOT NULL COMMENT 'B站id',
    `enabled` tinyint(1) NULL DEFAULT NULL,
    `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for live_off
-- ----------------------------
DROP TABLE IF EXISTS `live_off`;
CREATE TABLE `live_off`
(
    `id`      varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `uid`     bigint(0) NOT NULL COMMENT 'B站id',
    `enabled` tinyint(1) NULL DEFAULT NULL,
    `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for live_on
-- ----------------------------
DROP TABLE IF EXISTS `live_on`;
CREATE TABLE `live_on`
(
    `id`      varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `uid`     bigint(0) NOT NULL COMMENT 'B站id',
    `enabled` tinyint(1) NULL DEFAULT NULL,
    `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for live_report
-- ----------------------------
DROP TABLE IF EXISTS `live_report`;
CREATE TABLE `live_report`
(
    `id`                 varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `uid`                bigint(0) NOT NULL COMMENT 'b站id',
    `enabled`            tinyint(1) NULL DEFAULT NULL,
    `logo`               text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
    `logo_base64`        longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
    `time`               tinyint(1) NULL DEFAULT NULL,
    `fans_change`        tinyint(1) NULL DEFAULT NULL,
    `fans_medal_change`  tinyint(1) NULL DEFAULT NULL,
    `guard_change`       tinyint(1) NULL DEFAULT NULL,
    `danmu`              tinyint(1) NULL DEFAULT NULL,
    `box`                tinyint(1) NULL DEFAULT NULL,
    `gift`               tinyint(1) NULL DEFAULT NULL,
    `sc`                 tinyint(1) NULL DEFAULT NULL,
    `guard`              tinyint(1) NULL DEFAULT NULL,
    `danmu_ranking`      int(0) NULL DEFAULT NULL,
    `box_ranking`        int(0) NULL DEFAULT NULL,
    `box_profit_ranking` int(0) NULL DEFAULT NULL,
    `gift_ranking`       int(0) NULL DEFAULT NULL,
    `sc_ranking`         int(0) NULL DEFAULT NULL,
    `guard_list`         tinyint(1) NULL DEFAULT NULL,
    `box_profit_diagram` tinyint(1) NULL DEFAULT NULL,
    `danmu_diagram`      tinyint(1) NULL DEFAULT NULL,
    `box_diagram`        tinyint(1) NULL DEFAULT NULL,
    `gift_diagram`       tinyint(1) NULL DEFAULT NULL,
    `sc_diagram`         tinyint(1) NULL DEFAULT NULL,
    `guard_diagram`      tinyint(1) NULL DEFAULT NULL,
    `danmu_cloud`        tinyint(1) NULL DEFAULT NULL,
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for targets
-- ----------------------------
DROP TABLE IF EXISTS `targets`;
CREATE TABLE `targets`
(
    `id`      varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `uid`     bigint(0) NOT NULL COMMENT 'B站id',
    `num`     bigint(0) NULL DEFAULT NULL COMMENT '需要推送的推送目标 QQ 号或群号',
    `type`    int(10) UNSIGNED ZEROFILL NULL DEFAULT NULL COMMENT '推送类型，0 为私聊推送，1 为群聊推送',
    `uname`   text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
    `room_id` bigint(0) NULL DEFAULT NULL,
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

SET
FOREIGN_KEY_CHECKS = 1;
