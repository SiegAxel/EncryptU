import { PDFDocument, StandardFonts, rgb, PDFPage } from 'pdf-lib';
import * as ExcelJS from 'exceljs';

// Types for reports
export interface UserReportData {
  id: string;
  email: string;
  name: string;
  role: string;
  createdAt: Date;
  lastLogin?: Date;
  isActive: boolean;
  subscription?: {
    plan: string;
    status: string;
    startDate: Date;
    endDate?: Date;
  };
}

export interface TicketReportData {
  id: string;
  subject: string;
  description: string;
  status: 'open' | 'in_progress' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  createdAt: Date;
  updatedAt: Date;
  userId: string;
  userEmail: string;
  assignedTo?: string;
  resolutionTime?: number; // in hours
}

// PDF Generation Utilities
export class PDFReportGenerator {
  private pdfDoc!: PDFDocument;
  private page!: PDFPage;
  private yPosition!: number;
  private pageHeight!: number;
  private pageWidth!: number;
  private margin: number = 50;

  constructor() {
    this.margin = 50;
  }

  async initialize() {
    this.pdfDoc = await PDFDocument.create();
    this.pageHeight = 842; // A4 height
    this.pageWidth = 595;  // A4 width
    this.addNewPage();
    return this;
  }

  private addNewPage() {
    this.page = this.pdfDoc.addPage([this.pageWidth, this.pageHeight]);
    this.yPosition = this.pageHeight - this.margin;
  }

  private checkPageBreak(requiredHeight: number) {
    if (this.yPosition - requiredHeight < this.margin) {
      this.addNewPage();
    }
  }

  private async addHeader(title: string, subtitle?: string) {
    const font = await this.pdfDoc.embedFont(StandardFonts.HelveticaBold);
    const regularFont = await this.pdfDoc.embedFont(StandardFonts.Helvetica);

    // Title
    this.page.drawText(title, {
      x: this.margin,
      y: this.yPosition,
      size: 24,
      font: font,
      color: rgb(0.2, 0.2, 0.2),
    });
    this.yPosition -= 30;

    // Subtitle
    if (subtitle) {
      this.page.drawText(subtitle, {
        x: this.margin,
        y: this.yPosition,
        size: 14,
        font: regularFont,
        color: rgb(0.5, 0.5, 0.5),
      });
      this.yPosition -= 20;
    }

    // Line separator
    this.page.drawLine({
      start: { x: this.margin, y: this.yPosition },
      end: { x: this.pageWidth - this.margin, y: this.yPosition },
      thickness: 2,
      color: rgb(0.2, 0.2, 0.2),
    });
    this.yPosition -= 20;
  }

  private async addTable(headers: string[], data: (string | number | boolean | null | undefined)[][] , columnWidths: number[]) {
    const font = await this.pdfDoc.embedFont(StandardFonts.Helvetica);
    const boldFont = await this.pdfDoc.embedFont(StandardFonts.HelveticaBold);

    const rowHeight = 20;
    const headerHeight = 25;

    // Calculate total width and check if table fits
    const totalWidth = columnWidths.reduce((sum, width) => sum + width, 0);
    this.checkPageBreak(headerHeight + (data.length * rowHeight));

    // Headers
    let xPosition = this.margin;
    headers.forEach((header, index) => {
      this.page.drawText(header, {
        x: xPosition + 5,
        y: this.yPosition - 5,
        size: 10,
        font: boldFont,
        color: rgb(1, 1, 1),
      });
      xPosition += columnWidths[index];
    });

    // Header background
    this.page.drawRectangle({
      x: this.margin,
      y: this.yPosition - headerHeight,
      width: totalWidth,
      height: headerHeight,
      color: rgb(0.2, 0.2, 0.2),
    });

    this.yPosition -= headerHeight;

    // Data rows
    data.forEach((row) => {
      xPosition = this.margin;
      row.forEach((cell, index) => {
        const cellText = String(cell || '');
        const truncatedText = cellText.length > 20 ? cellText.substring(0, 20) + '...' : cellText;
        
        this.page.drawText(truncatedText, {
          x: xPosition + 5,
          y: this.yPosition - 5,
          size: 9,
          font: font,
          color: rgb(0, 0, 0),
        });
        xPosition += columnWidths[index];
      });

      // Row separator
      this.page.drawLine({
        start: { x: this.margin, y: this.yPosition },
        end: { x: this.margin + totalWidth, y: this.yPosition },
        thickness: 0.5,
        color: rgb(0.8, 0.8, 0.8),
      });

      this.yPosition -= rowHeight;
    });

    this.yPosition -= 10;
  }

  async generateUsersReport(users: UserReportData[], title = 'Users Report') {
    await this.initialize();
    await this.addHeader(title, `Total Users: ${users.length}`);

    const headers = ['Email', 'Name', 'Role', 'Status', 'Created', 'Last Login', 'Subscription'];
    const data = users.map(user => [
      user.email,
      user.name,
      user.role,
      user.isActive ? 'Active' : 'Inactive',
      user.createdAt.toLocaleDateString(),
      user.lastLogin?.toLocaleDateString() || 'Never',
      user.subscription?.plan || 'Free'
    ]);

    const columnWidths = [120, 100, 80, 70, 80, 80, 80];
    await this.addTable(headers, data, columnWidths);

    const pdfBytes = await this.pdfDoc.save();
    return pdfBytes;
  }

  async generateTicketsReport(tickets: TicketReportData[], title = 'Support Tickets Report') {
    await this.initialize();
    await this.addHeader(title, `Total Tickets: ${tickets.length}`);

    const headers = ['Subject', 'Status', 'Priority', 'Created', 'User', 'Resolution Time'];
    const data = tickets.map(ticket => [
      ticket.subject,
      ticket.status,
      ticket.priority,
      ticket.createdAt.toLocaleDateString(),
      ticket.userEmail,
      ticket.resolutionTime ? `${ticket.resolutionTime}h` : 'Open'
    ]);

    const columnWidths = [150, 80, 70, 80, 120, 80];
    await this.addTable(headers, data, columnWidths);

    const pdfBytes = await this.pdfDoc.save();
    return pdfBytes;
  }
}

// Excel Generation Utilities
export class ExcelReportGenerator {
  private workbook: ExcelJS.Workbook;

  constructor() {
    this.workbook = new ExcelJS.Workbook();
  }

  async generateUsersReport(users: UserReportData[]) {
    const worksheet = this.workbook.addWorksheet('Users Report');

    // Headers
    worksheet.columns = [
      { header: 'Email', key: 'email', width: 30 },
      { header: 'Name', key: 'name', width: 20 },
      { header: 'Role', key: 'role', width: 15 },
      { header: 'Status', key: 'status', width: 12 },
      { header: 'Created Date', key: 'createdAt', width: 15 },
      { header: 'Last Login', key: 'lastLogin', width: 15 },
      { header: 'Subscription Plan', key: 'subscription', width: 20 },
      { header: 'Subscription Status', key: 'subscriptionStatus', width: 20 }
    ];

    // Style headers
    worksheet.getRow(1).font = { bold: true, color: { argb: 'FFFFFF' } };
    worksheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: '366092' }
    };

    // Add data
    users.forEach(user => {
      worksheet.addRow({
        email: user.email,
        name: user.name,
        role: user.role,
        status: user.isActive ? 'Active' : 'Inactive',
        createdAt: user.createdAt.toLocaleDateString(),
        lastLogin: user.lastLogin?.toLocaleDateString() || 'Never',
        subscription: user.subscription?.plan || 'Free',
        subscriptionStatus: user.subscription?.status || 'N/A'
      });
    });

    // Auto-fit columns
    worksheet.columns.forEach(column => {
      column.width = Math.max(column.width || 10, 15);
    });

    return this.workbook;
  }

  async generateTicketsReport(tickets: TicketReportData[]) {
    const worksheet = this.workbook.addWorksheet('Tickets Report');

    // Headers
    worksheet.columns = [
      { header: 'Subject', key: 'subject', width: 40 },
      { header: 'Status', key: 'status', width: 15 },
      { header: 'Priority', key: 'priority', width: 12 },
      { header: 'Created Date', key: 'createdAt', width: 15 },
      { header: 'User Email', key: 'userEmail', width: 30 },
      { header: 'Assigned To', key: 'assignedTo', width: 20 },
      { header: 'Resolution Time (hrs)', key: 'resolutionTime', width: 20 }
    ];

    // Style headers
    worksheet.getRow(1).font = { bold: true, color: { argb: 'FFFFFF' } };
    worksheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: '366092' }
    };

    // Add data
    tickets.forEach(ticket => {
      worksheet.addRow({
        subject: ticket.subject,
        status: ticket.status,
        priority: ticket.priority,
        createdAt: ticket.createdAt.toLocaleDateString(),
        userEmail: ticket.userEmail,
        assignedTo: ticket.assignedTo || 'Unassigned',
        resolutionTime: ticket.resolutionTime || 'Open'
      });
    });

    // Auto-fit columns
    worksheet.columns.forEach(column => {
      column.width = Math.max(column.width || 10, 15);
    });

    return this.workbook;
  }
}