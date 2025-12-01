import { NextResponse, type NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { requireAdmin } from '@/app/api/admin/requireAdmin';
import { PDFReportGenerator, ExcelReportGenerator } from '@/lib/reports';

export const runtime = "nodejs";

// Adjust the interface to match the actual database schema
interface UserReportData {
  id: number; // Changed from string to number to match actual schema
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

// GET /api/admin/reports/users
export async function GET(request: NextRequest) {
  try {
    const me = await requireAdmin();
    if (!me) {
      return NextResponse.json({ ok: false, error: "Forbidden" }, { status: 403 });
    }

    const { searchParams } = new URL(request.url);
    const format = searchParams.get('format') || 'pdf'; // pdf or excel
    const startDate = searchParams.get('startDate');
    const endDate = searchParams.get('endDate');
    // const role = searchParams.get('role'); // admin, soporte, usuario - commented out as it's not used

    // Construir cláusula WHERE
    const whereClause: any = {}; // eslint-disable-line @typescript-eslint/no-explicit-any
    
    if (startDate || endDate) {
      whereClause.createdAt = {};
      if (startDate) whereClause.createdAt.gte = new Date(startDate);
      if (endDate) whereClause.createdAt.lte = new Date(endDate);
    }

    // Note: role filtering not available in current schema

    // Fetch users
    const users = await prisma.user.findMany({
      where: whereClause,
      orderBy: {
        createdAt: 'desc'
      }
    });

    // Transform data for reports - use actual fields from User model
    const reportData: UserReportData[] = users.map(user => ({
      id: user.id, // Now matches number type
      email: user.email,
      name: user.name, // Usar el campo de nombre real del modelo User
      role: user.role, // Usar el campo role real del modelo User
      createdAt: user.createdAt,
      lastLogin: undefined, // Not available in current schema
      isActive: true, // Not available in current schema, assume all users are active
      subscription: undefined // Subscription data not available in current schema
    }));

    if (format === 'excel') {
      const excelGenerator = new ExcelReportGenerator();
      const workbook = await excelGenerator.generateUsersReport(reportData);
      
      // Convert to buffer
      const buffer = await workbook.xlsx.writeBuffer();
      
      return new NextResponse(buffer, {
        headers: {
          'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'Content-Disposition': `attachment; filename="users-report-${new Date().toISOString().split('T')[0]}.xlsx"`
        }
      });
    } else {
      // Default to PDF
      const pdfGenerator = new PDFReportGenerator();
      const pdfBytes = await pdfGenerator.generateUsersReport(reportData);
      
      return new NextResponse(Buffer.from(pdfBytes), {
        headers: {
          'Content-Type': 'application/pdf',
          'Content-Disposition': `attachment; filename="users-report-${new Date().toISOString().split('T')[0]}.pdf"`
        }
      });
    }

  } catch (error) {
    console.error('Error generating users report:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}