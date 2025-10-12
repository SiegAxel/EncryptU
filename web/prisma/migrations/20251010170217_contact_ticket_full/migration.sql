/*
  Warnings:

  - You are about to drop the column `message` on the `ContactTicket` table. All the data in the column will be lost.
  - You are about to drop the column `name` on the `ContactTicket` table. All the data in the column will be lost.
  - Added the required column `description` to the `ContactTicket` table without a default value. This is not possible if the table is not empty.
  - Added the required column `firstName` to the `ContactTicket` table without a default value. This is not possible if the table is not empty.
  - Added the required column `lastName` to the `ContactTicket` table without a default value. This is not possible if the table is not empty.
  - Added the required column `phone` to the `ContactTicket` table without a default value. This is not possible if the table is not empty.
  - Added the required column `reason` to the `ContactTicket` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "ContactTicket" DROP COLUMN "message",
DROP COLUMN "name",
ADD COLUMN     "description" TEXT NOT NULL,
ADD COLUMN     "firstName" TEXT NOT NULL,
ADD COLUMN     "lastName" TEXT NOT NULL,
ADD COLUMN     "phone" TEXT NOT NULL,
ADD COLUMN     "reason" TEXT NOT NULL;