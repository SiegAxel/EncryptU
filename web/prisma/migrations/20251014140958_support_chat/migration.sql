/*
  Warnings:

  - You are about to drop the column `message` on the `ContactTicket` table. All the data in the column will be lost.
  - You are about to drop the column `name` on the `ContactTicket` table. All the data in the column will be lost.
  - The `role` column on the `User` table would be dropped and recreated. This will lead to data loss if there is data in the column.
  - Added the required column `description` to the `ContactTicket` table without a default value. This is not possible if the table is not empty.
  - Added the required column `firstName` to the `ContactTicket` table without a default value. This is not possible if the table is not empty.
  - Added the required column `lastName` to the `ContactTicket` table without a default value. This is not possible if the table is not empty.
  - Added the required column `phone` to the `ContactTicket` table without a default value. This is not possible if the table is not empty.
  - Added the required column `reason` to the `ContactTicket` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "ContactTicket" DROP COLUMN "message",
DROP COLUMN "name",
ADD COLUMN     "assignedToId" INTEGER,
ADD COLUMN     "description" TEXT NOT NULL,
ADD COLUMN     "firstName" TEXT NOT NULL,
ADD COLUMN     "lastName" TEXT NOT NULL,
ADD COLUMN     "phone" TEXT NOT NULL,
ADD COLUMN     "reason" TEXT NOT NULL,
ADD COLUMN     "status" TEXT NOT NULL DEFAULT 'open';

-- AlterTable
ALTER TABLE "User" DROP COLUMN "role",
ADD COLUMN     "role" TEXT NOT NULL DEFAULT 'usuario';

-- DropEnum
DROP TYPE "public"."Role";

-- CreateTable
CREATE TABLE "TicketMessage" (
    "id" SERIAL NOT NULL,
    "ticketId" INTEGER NOT NULL,
    "author" TEXT NOT NULL,
    "name" TEXT,
    "email" TEXT,
    "body" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "TicketMessage_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "ContactTicket" ADD CONSTRAINT "ContactTicket_assignedToId_fkey" FOREIGN KEY ("assignedToId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TicketMessage" ADD CONSTRAINT "TicketMessage_ticketId_fkey" FOREIGN KEY ("ticketId") REFERENCES "ContactTicket"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
