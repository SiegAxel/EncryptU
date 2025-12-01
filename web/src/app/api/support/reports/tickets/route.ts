import { NextResponse, type NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { requireAgent } from '@/app/api/support/requireAgent';
import { PDFReportGenerator, ExcelReportGenerator } from '@/lib/reports';

export const runtime = "nodejs";

// Adjust the interface to match the actual database schema
interface TicketReportData {
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

// GET /api/support/reports/tickets
export async function GET(request: NextRequest) {
  try {
    const me = await requireAgent();
    if (!me) {
      return NextResponse.json({ ok: false, error: "Forbidden" }, { status: 403 });
    }

    const { searchParams } = new URL(request.url);
    const format = searchParams.get('format') || 'pdf'; // pdf or excel
    const startDate = searchParams.get('startDate');
    const endDate = searchParams.get('endDate');
    const status = searchParams.get('status'); // open, in_progress, closed
    const priority = searchParams.get('priority'); // low, medium, high, urgent
    const assignedTo = searchParams.get('assignedTo'); // ID de usuario o 'me'

    // Construir cláusula WHERE
    const whereClause: any = {}; // eslint-disable-line @typescript-eslint/no-explicit-any
    
    if (startDate || endDate) {
      whereClause.createdAt = {};
      if (startDate) whereClause.createdAt.gte = new Date(startDate);
      if (endDate) whereClause.createdAt.lte = new Date(endDate);
    }

    if (status && ['open', 'in_progress', 'closed'].includes(status)) {
      whereClause.status = status;
    }

    if (priority && ['low', 'medium', 'high', 'urgent'].includes(priority)) {
      whereClause.priority = priority;
    }

    if (assignedTo === 'me') {
      whereClause.assignedToId = me.id;
    } else if (assignedTo && !isNaN(Number(assignedTo))) {
      whereClause.assignedToId = Number(assignedTo);
    }

    // Fetch tickets with related data
    const tickets = await prisma.contactTicket.findMany({
      where: whereClause,
      include: {
        assignedTo: {
          select: {
            name: true,
            email: true
          }
        },
        messages: {
          select: {
            createdAt: true,
            author: true
          },
          orderBy: {
            createdAt: 'desc'
          },
          take: 1 // Get the last message for resolution time calculation
        }
      },
      orderBy: {
        createdAt: 'desc'
      }
    });

    // Transform data for reports
    const reportData: TicketReportData[] = tickets.map(ticket => {
      const lastMessage = ticket.messages[0];
      let resolutionTime: number | undefined;

      if (lastMessage && ticket.status === 'closed') {
        // Calculate resolution time in hours
        const createdTime = ticket.createdAt.getTime();
        const resolvedTime = lastMessage.createdAt.getTime();
        resolutionTime = Math.round((resolvedTime - createdTime) / (1000 * 60 * 60)); // Convert to hours
      }

      return {
        id: ticket.id.toString(),
        subject: `${ticket.firstName} ${ticket.lastName} - ${ticket.reason}`,
        description: ticket.description,
        status: ticket.status as 'open' | 'in_progress' | 'closed',
        priority: 'medium', // Default priority as it's not in the schema
        createdAt: ticket.createdAt,
        updatedAt: lastMessage?.createdAt || ticket.createdAt,
        userId: ticket.email, // Usar email como identificador ya que no tenemos ID de usuario
        userEmail: ticket.email,
        assignedTo: ticket.assignedTo?.name,
        resolutionTime
      };
    });

    if (format === 'excel') {
      const excelGenerator = new ExcelReportGenerator();
      const workbook = await excelGenerator.generateTicketsReport(reportData);
      
      // Convert to buffer
      const buffer = await workbook.xlsx.writeBuffer();
      
      return new NextResponse(buffer, {
        headers: {
          'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'Content-Disposition': `attachment; filename="tickets-report-${new Date().toISOString().split('T')[0]}.xlsx"`
        }
      });
    } else {
      // Default to PDF
      const pdfGenerator = new PDFReportGenerator();
      const pdfBytes = await pdfGenerator.generateTicketsReport(reportData);
      
      return new NextResponse(Buffer.from(pdfBytes), {
        headers: {
          'Content-Type': 'application/pdf',
          'Content-Disposition': `attachment; filename="tickets-report-${new Date().toISOString().split('T')[0]}.pdf"`
        }
      });
    }

  } catch (error) {
    console.error('Error generating tickets report:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}