SELECT U.id, TP.Id_personal, 
				  TC.NEmpleado_co, 
				  U.username, 
				  U.password, 
				  TP.Nombre_ps, 
				  TP.APaterno_ps, 
				  TP.AMaterno_ps, 
				  U.is_superuser, 
				  U.first_name + ' ' + U.last_name AS NombreCompleto, 
				  U.email, 
				  U.date_joined, 
				  TP.RutaFoto_ps, 
                  TCat.Nombre_ct, 
                  CASE TC.Direccion_co 
				  WHEN 5 THEN 'Administración' 
				  WHEN 26 THEN 'Calidad, Ambiental, Seguridad y Salud' 
				  WHEN 70 THEN 'Presidencia Grupo IAI' 
				  WHEN 71 THEN 'Proyectos Especiales' 
				  WHEN 84 THEN 'Direccion de Proyectos Convencionales'
                  WHEN 99 THEN 'Ingeniería' 
				  WHEN 105 THEN 'Tecnatom' 
				  ELSE CAST(TC.Direccion_co AS VARCHAR) 
				  END AS nombre_direccion, 
				  'coordinacion aun por definir su origen' AS nombre_coordinacion, 
				  U.is_active, 
				  TP.nombreSupervisor, 
                  TP.Supervisor_co , 
				--  RC.ProyectoActualEmpleado ,
				--  RC.EstadoEmpleado, 
				  CASE 
						WHEN  TP.Status_ps = 3 AND  TP.Status_co = 2 AND TC.Historial_co=1 THEN 'Nomina apoyo'
						WHEN  TP.Status_ps = 3 AND  TP.Status_co = 1 AND TC.Historial_co=1 THEN 'Contratado'
						WHEN  TP.Status_ps = 2  THEN 'Reclutado'
						WHEN  TP.Status_ps = 1   THEN  'Pasivo'
				  END  AS EstadoEmpleado ,   
				  CASE 
						WHEN CR.Proyecto_rt IS NOT NULL AND TP.Proyecto_co IS  NULL  THEN CR.Proyecto_rt 
						WHEN CR.Proyecto_rt = TP.Proyecto_co THEN CR.Proyecto_rt 
						WHEN CR.Proyecto_rt IS NOT NULL AND TP.Proyecto_co IS NOT NULL AND CR.Proyecto_rt != TP.Proyecto_co THEN TP.Proyecto_co
				  END AS ProyectoActualEmpleado 
				  --TP.Proyecto_co

FROM     dbo.auth_user AS U RIGHT OUTER JOIN
                  SERCAP.dbo.vconsultaContratacion AS TP ON TP.Nombre_ps = U.first_name COLLATE SQL_LATIN1_GENERAL_CP1_CI_AI AND 
                  TP.APaterno_ps + ' ' + TP.AMaterno_ps = U.last_name COLLATE SQL_LATIN1_GENERAL_CP1_CI_AI INNER JOIN
                  SERCAP.dbo.TContratos AS TC ON TC.Id_personal = TP.Id_personal AND TC.Historial_co = 1 INNER JOIN
                  SERCAP.dbo.TCategorias AS TCat ON TCat.Id_categoria = TC.Categoria_co  
				  -- LEFT JOIN  SERCAP.dbo.vRECOL AS RC ON RC.Id_personal = TC.Id_personal  
			     INNER JOIN SERCAP.dbo.TProcesoReclutamiento AS CR ON CR.Id_personal =  TP.Id_personal




                 use IDIAI_v2

SELECT      TODOSP.Id_personal
					--,N_EMPLEADO.NEmpleado_co
					,CASE 
						WHEN N_EMPLEADO.NEmpleado_co IS NULL THEN 'S/N'
						ELSE CAST(N_EMPLEADO.NEmpleado_co AS varchar ) END AS NEmpleado_co
					, TODOSP.Nombre_ps, TODOSP.APaterno_ps , TODOSP.AMaterno_ps
					,TODOSP.APaterno_ps+' '+TODOSP.AMaterno_ps+' '+TODOSP.Nombre_ps as NOMBRE_COMPLETO
					,CASE 
						WHEN  TODOSP.Status_ps = 3 AND  TODOSC.Status_co = 2 AND TODOSC.Historial_co=1 THEN 'Nomina apoyo'
						WHEN  TODOSP.Status_ps = 3 AND  TODOSC.Status_co = 1 AND TODOSC.Historial_co=1 THEN 'Contratado'
						WHEN  TODOSP.Status_ps = 2  THEN 'Reclutado'
						WHEN  TODOSP.Status_ps = 1   THEN  'Pasivo'
							END  AS 
							EstadoEmpleado,
					  /*CASE
						WHEN TODOSR.Categoria_rt IS NOT NULL AND TODOSC.Categoria_co IS  NULL THEN TODOSR.Categoria_rt 
						WHEN TODOSR.Categoria_rt = TODOSC.Categoria_co THEN TODOSR.Proyecto_rt 
						WHEN TODOSR.Categoria_rt IS NOT NULL AND TODOSC.Categoria_co IS NOT NULL AND TODOSR.Categoria_rt != TODOSC.Categoria_co THEN TODOSC.Categoria_co
						END AS CategoriaIAIActual,*/
					  CASE 
						WHEN TODOSR.Proyecto_rt IS NOT NULL AND TODOSC.Proyecto_co IS  NULL  THEN TODOSR.Proyecto_rt 
						WHEN TODOSR.Proyecto_rt = TODOSC.Proyecto_co THEN TODOSR.Proyecto_rt 
						WHEN TODOSR.Proyecto_rt IS NOT NULL AND TODOSC.Proyecto_co IS NOT NULL AND TODOSR.Proyecto_rt != TODOSC.Proyecto_co THEN TODOSC.Proyecto_co
						END AS ProyectoActualEmpleado
FROM				  SERCAP.dbo.TPersonal AS TODOSP 
			LEFT OUTER JOIN
					  --dbo.TDatosCLV AS TODOSCLV ON TODOSP.Id_personal = TODOSCLV.Id_personal LEFT OUTER JOIN
                      SERCAP.dbo.TGafetesCLV AS TGAFETECLV ON TODOSP.Id_personal = TGAFETECLV.Id_personal 
		LEFT OUTER JOIN
					  SERCAP.dbo.TLiberacionCLV AS TLIBERCLV ON TLIBERCLV.Id_personal = TODOSP.Id_personal 
					  LEFT  JOIN
                      SERCAP.dbo.TExpedienteCLV AS TEXPEDCLV ON TODOSP.Id_personal = TEXPEDCLV.Id_personal 
					  LEFT  JOIN
                      (SELECT  DISTINCT(Id_personal), [NumIFE_ip] FROM [TInformePersonalCLV]) AS INE ON INE.Id_personal = TODOSP.Id_personal 
					  LEFT  JOIN dbo.TCategorias AS TCategorias_1 
					  RIGHT  JOIN
                          (SELECT     Id_tramite, Id_personal, FITramites_rt, TipoAnexo_rt, FolioAnexo_rt, Proyecto_rt, Categoria_rt, ModoIngreso_rt, TipoIngreso_rt, LiberacionQA_rt, 
                                                   ConSISCOP_rt, Experiencia_rt, Id_requisicion, Consecutivo_rp, Numero_rc, Unidad_rc, Historial_rt, Califica_rt, Proveedor_rt,Consecutivo_d
                            FROM          dbo.TProcesoReclutamiento AS PR1
                            WHERE      (Id_tramite =
                                                       (SELECT     MAX(Id_tramite) AS Valor
                                                         FROM          dbo.TProcesoReclutamiento AS PR2
                                                         WHERE      (PR1.Id_personal = Id_personal)))) AS TODOSR ON TCategorias_1.Id_categoria = TODOSR.Categoria_rt ON 
                      TODOSP.Id_personal = TODOSR.Id_personal
					  LEFT  JOIN SERCAP.dbo.TCategorias AS TCategorias_2 
					  RIGHT  JOIN
                          (SELECT     Id_contrato, Id_personal, NEmpleado_co, Proyecto_co, Categoria_co, Status_co, Direccion_co, Gerencia_co, LugarTrabajo_co, Id_registropatronal, 
                                                   Tipo_con, FContratacion_co, FIngreso_co, FVigencia_co, Supervisor_co, SDiario_co, SDImss_co, SBase_co, SBLetra_co, TipoNomina_co, 
                                                   FormaPago_co, Id_requisicion_co, Consecutivo_co, FBaja_co, Historial_co, UsuarioContratista, UsuarioBaja, FInicioLabores_co, AsignacionPaquete_co, 
                                                   Destino_co, Ruta_co, HLInicio_co, HLTermino_co, Turno_co, CompaniaTrabajo_co, FechaGafete_co, Disciplina_co, DiasVacaciones, DiasRestantes, 
                                                   Rendimiento_co, ObservacionesRen_co, Firmado_co, ModCont_co, EstPersProy_co,consecutivo_d
                            FROM          SERCAP.dbo.TContratos AS PC1
                            WHERE      (Id_contrato =
                                                       (SELECT     MAX(Id_contrato) AS Valor
                                                         FROM          dbo.TContratos
                                                         WHERE      (PC1.Id_personal = Id_personal))) and Historial_co =1) AS TODOSC ON TCategorias_2.Id_categoria = TODOSC.Categoria_co ON 
                      TODOSP.Id_personal = TODOSC.Id_personal
					  LEFT  JOIN
                          (SELECT      Id_personal, NEmpleado_co
                            FROM          dbo.TContratos AS N_EMP
                            WHERE      (Id_contrato =
                                                       (SELECT     MAX(Id_contrato) AS Valor
                                                         FROM          dbo.TContratos 
                                                         WHERE      (N_EMP.Id_personal = Id_personal))) ) AS N_EMPLEADO ON   TODOSP.Id_personal = N_EMPLEADO.Id_personal
					  LEFT OUTER JOIN
                      SERCAP.dbo.TCategorias AS PERCAT ON PERCAT.Id_categoria =
							CASE WHEN TODOSC.Categoria_co IS NULL  THEN TODOSR.Categoria_rt
								ELSE TODOSC.Categoria_co END
						LEFT OUTER JOIN                     
                      SERCAP.dbo.TPsicometricos AS TODOSPSI ON TODOSPSI.Id_tramite = TODOSR.Id_tramite LEFT OUTER JOIN
                      SERCAP.dbo.TCapacitacion AS TODOSCAP ON TODOSCAP.Id_tramite = TODOSR.Id_tramite LEFT OUTER JOIN
                      SERCAP.dbo.TLiberacionCLV AS TODOSLIB ON TODOSLIB.Id_tramite = TODOSR.Id_tramite  
					   LEFT  JOIN bdidiai.dbo.USUARIOS AS USUARIOS_3 ON  TODOSC.Supervisor_co COLLATE Modern_Spanish_CI_AS = USUARIOS_3.usuario
					   LEFT JOIN ( SELECT  
									Proyecto_rp,[FRegistro_rp],Id_requisicion,Consecutivo_rp,[TipoCLV_rp]
									FROM TRequisicionesPersonal WHERE   (Status_rp < 3) 
									GROUP BY Proyecto_rp,[FRegistro_rp],Id_requisicion,Consecutivo_rp,[TipoCLV_rp]) AS TReqPer ON  TReqPer.Proyecto_rp = (
																							SELECT TOP 1 Proyecto_rp
																							FROM TRequisicionesPersonal
																							WHERE Proyecto_rp = CASE
																													WHEN TODOSR.Proyecto_rt IS NOT NULL AND TODOSC.Proyecto_co IS  NULL THEN TODOSR.Proyecto_rt 
																													WHEN TODOSR.Proyecto_rt = TODOSC.Proyecto_co THEN TODOSR.Proyecto_rt 
																													WHEN TODOSR.Proyecto_rt IS NOT NULL AND TODOSC.Proyecto_co IS NOT NULL AND TODOSR.Proyecto_rt != TODOSC.Proyecto_co THEN TODOSC.Proyecto_co
																													END 
																							GROUP BY Proyecto_rp
																						)   
																						AND TReqPer.[FRegistro_rp] =(
																							SELECT TOP 1 [FRegistro_rp]
																							FROM TRequisicionesPersonal
																							WHERE Proyecto_rp = CASE
																													WHEN TODOSR.Proyecto_rt IS NOT NULL AND TODOSC.Proyecto_co IS  NULL THEN TODOSR.Proyecto_rt 
																													WHEN TODOSR.Proyecto_rt = TODOSC.Proyecto_co THEN TODOSR.Proyecto_rt 
																													WHEN TODOSR.Proyecto_rt IS NOT NULL AND TODOSC.Proyecto_co IS NOT NULL AND TODOSR.Proyecto_rt != TODOSC.Proyecto_co THEN TODOSC.Proyecto_co
																													END 
																							GROUP BY [FRegistro_rp]
																						)   
JOIN   [vProyectosCostos] vPC ON 
			CASE --SELECCIONA PROYECTO ACTUAL
						WHEN TODOSR.Proyecto_rt IS NOT NULL AND TODOSC.Proyecto_co IS  NULL THEN TODOSR.Proyecto_rt 
						WHEN TODOSR.Proyecto_rt = TODOSC.Proyecto_co THEN TODOSR.Proyecto_rt 
						WHEN TODOSR.Proyecto_rt IS NOT NULL AND TODOSC.Proyecto_co IS NOT NULL AND TODOSR.Proyecto_rt != TODOSC.Proyecto_co THEN TODOSC.Proyecto_co
						END =vPC.proyecto COLLATE SQL_Latin1_General_CP437_BIN
		--TODOSR.Proyecto_rt = vPC.proyecto COLLATE SQL_Latin1_General_CP437_BIN  
--and (vPC.[direccionProyecto] ='DIRECCION DE INGENIERÍA' )
--and (vPC.[direccionProyecto] ='DIRECCION DE INGENIERÍA' OR vPC.[direccionProyecto] ='DIRECCION DE ADMINISTRACION')
and TODOSP.Status_ps !=1--DIFERENTE DE PASIVO
left JOIN TDetalleRequisiciones  TDR ON PERCAT.Id_categoria=TDR.Categoria_d 
	AND TDR.Id_requisicion = CASE
								WHEN TODOSR.Historial_rt = 1 AND TDR.Consecutivo_d=TODOSR.Consecutivo_d THEN TODOSR.Id_requisicion 
								WHEN TODOSC.Historial_co = 1 AND TDR.Consecutivo_d=TODOSC.consecutivo_d THEN TODOSC.Id_requisicion_co
								ELSE TODOSR.Id_requisicion END
	AND TDR.Consecutivo_rp = CASE
								WHEN TODOSR.Historial_rt = 1 AND TDR.Consecutivo_d=TODOSR.Consecutivo_d THEN TODOSR.Consecutivo_rp 
								WHEN TODOSC.Historial_co = 1 AND TDR.Consecutivo_d=TODOSC.consecutivo_d THEN TODOSC.Consecutivo_co
								ELSE TODOSR.Consecutivo_rp END
	AND TDR.Consecutivo_d = CASE
								WHEN TODOSR.Historial_rt = 1 AND TDR.Consecutivo_d=TODOSR.Consecutivo_d THEN TODOSR.Consecutivo_d 
								WHEN TODOSC.Historial_co = 1 AND TDR.Consecutivo_d=TODOSC.consecutivo_d THEN TODOSC.consecutivo_d
								ELSE TODOSR.Consecutivo_d  END
								--WHERE vPC.proyecto='IN-GEH-002/23'


SELECT TOP (1000) [id]
      ,[_nombre]
      ,[_descripcion]
      ,[nombre_completo]
  FROM [IDIAI_v2].[dbo].[TRegistroDeModulo]  where  [nombre_completo]= 'Abraham Barrios Jiménez'

  delete
  FROM [IDIAI_v2].[dbo].[TRegistroDeModulo]

  SELECT nombre_completo, COUNT(*) as Repetidos
FROM [IDIAI_v2].[dbo].[TRegistroDeModulo]
GROUP BY nombre_completo
HAVING COUNT(*) > 1
ORDER BY Repetidos DESC;

DELETE FROM [IDIAI_v2].[dbo].[TRegistroDeModulo]
WHERE id = 7601